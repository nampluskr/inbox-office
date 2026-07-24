#include "StdAfx.h"
#include "FFTLog.h"
#include <queue>

CMacroFFTLog::CMacroFFTLog(MIL_ID milSystem, void* pParent)
{
	m_MilSystem = milSystem;
	m_pParent = pParent;
}

CMacroFFTLog::~CMacroFFTLog(void)
{

}

void CMacroFFTLog::FFTMethod(MIL_ID milSrc)
{
	//bool bSave = true;
	bool bSave = false;

	const int avgRefFiltSize = 10;
	const int avgBGFiltSize = 48;
	const int ROI_x = 1170;
	const int ROI_y = 474;
	const int ROI_y_Total = 474;
	const int division_y = 1;

	int w = MbufInquire(milSrc, M_SIZE_X, M_NULL);
	int h = MbufInquire(milSrc, M_SIZE_Y, M_NULL);

	// 이미지 회전 진행 (Hole 오른쪽에 누운 Image 남음)
	cv::Mat cvSrc(h, w, CV_16U);
	MbufGet(milSrc, cvSrc.data);
	cv::Mat cvRotate;
	cv::transpose(cvSrc, cvRotate);     // 전치
	cv::flip(cvRotate, cvRotate, 0);       // 0: 상하 반전 → 반시계 방향 90 도 회전

	cv::Mat cvRotate32;
	cvRotate.convertTo(cvRotate32, CV_32F);

	// Width <> Height (90 도 회전 됐으므로)
	int rotated_w = h;
	int rotated_h_divided = w / 3;

	double* dProjRef = new double[ROI_x]; // Ref(AVG Filter 10 - Noise 제거) Proj. Data
	double* dProjBG = new double[ROI_x];  // BG(AVG Filter 48 - BackGround Data) Proj. Data
	
	for (int i = 0; i <= division_y; i++)
	{
		// Image 3 등분 해서 진행
		cv::Mat child;
		cv::Rect roi;
		if (i == division_y)
		{
			roi = cv::Rect(130, 60, ROI_x, ROI_y_Total);
		}
		else
		{
			roi = cv::Rect(0, rotated_h_divided * i, rotated_w, rotated_h_divided);
		}
		child = cvRotate32(roi); // ROI 참조

		// 각 Division 에 Filter 진행
		cv::Mat childRef;
		cv::Mat childGB;
		blur(child, childRef, cv::Size(avgRefFiltSize, avgRefFiltSize));
		blur(child, childGB, cv::Size(avgBGFiltSize, avgBGFiltSize));
		
		if (i == division_y)
		{
			GetProjection(childRef, 0, 0 / 2, ROI_x, ROI_y_Total, dProjRef); // Ref Proj. Data 남김
			GetProjection(childGB, 0, 0 / 2, ROI_x, ROI_y_Total, dProjBG); // BG Proj. Data 남김
		}
		else
		{
			GetProjection(childRef, (rotated_w - ROI_x) / 2, (rotated_h_divided - ROI_y) / 2, ROI_x, ROI_y, dProjRef); // Ref Proj. Data 남김
			GetProjection(childGB, (rotated_w - ROI_x) / 2, (rotated_h_divided - ROI_y) / 2, ROI_x, ROI_y, dProjBG); // BG Proj. Data 남김
		}

		cv::Mat result(ROI_x, 1, CV_64F);

		for (int iter = 0; iter < ROI_x; iter++)
			result.at<double>(iter, 0) = (dProjRef[iter] - dProjBG[iter]) / dProjBG[iter] * 100.; // Ref - BG / BG Ratio Data

		cv::Mat fftMag = computeFFTMagnitude(result);

		// 이번 셀은 32, 37 고정인데 이미지 사이즈 마다 달라지는지 확인 필요
		m_result.value35[i] = max(max(fftMag.at<double>(36, 0), fftMag.at<double>(37, 0)), fftMag.at<double>(38, 0));
		m_result.value40[i] = max(max(fftMag.at<double>(31, 0), fftMag.at<double>(32, 0)), fftMag.at<double>(33, 0));
		double mean40 = 0.0;
		for (int i = 0; i < 6; i++)
		{
			mean40 += fftMag.at<double>(31 + i, 0);
		}
		mean40 /= 6;
		if (m_result.value40[i] / mean40 < 1.35)
		{
			m_result.state[i] = 1;
		}
		else
		{
			m_result.state[i] = 2;
		}
	}
	
	SAFE_DEL_ARRAY(dProjBG);
	SAFE_DEL_ARRAY(dProjRef);
}

int CMacroFFTLog::GetFFTSize(int n)
{
	int nRtn = 1;
	while (nRtn <= n)
	{
		nRtn *= 2;
	}
	return nRtn;
}

void CMacroFFTLog::GetProjection(cv::Mat Src, int nSx, int nSy, int nW, int nH, double* dProj)
{
	cv::Rect roi(nSx, nSy, nW, nH);
	cv::Mat child = Src(roi); // ROI 참조

	// 수직 방향 (세로축) 합산: 각 열 (column) 의 합
	cv::Mat proj;
	reduce(child, proj, 0, CV_REDUCE_SUM, CV_64F);  // 0: 행 축소 → 열 기준 합산

	// 결과를 배열에 저장
	for (int i = 0; i < proj.cols; i++)
		dProj[i] = proj.at<double>(0, i);
}

cv::Mat CMacroFFTLog::computeFFTMagnitude(const cv::Mat& src)
{
	// 실수 신호 → 복소 출력
	cv::Mat complex;
	cv::dft(src, complex, cv::DFT_COMPLEX_OUTPUT);

	// 4) magnitude = sqrt(Re² + Im²)
	cv::Mat planes[2];
	cv::split(complex, planes);
	cv::Mat magnitude;
	cv::magnitude(planes[0], planes[1], magnitude);

	// 5) MATLAB 과 동일한 스케일 정규화
	//magnitude /= src.rows;

	// 6) MATLAB: profile_fft = magnitude(2 : floor(N/2));
	// C++ rowRange 는 [start, end) 이므로 rowRange(1, N/2)
	cv::Mat magHalf = magnitude.rowRange(1, src.rows / 2).clone();

	return magHalf; // CV_32F, (N/2-1) x 1
}
