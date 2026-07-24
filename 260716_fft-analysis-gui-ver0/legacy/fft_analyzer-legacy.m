list = dir('*.mim');

data = [];

s = 0;

for n = 1:size(list,1)

    fileName = list(n).name;

    avgFiltSize = 10;           % Noise 제거 Filter 크기
    avgRefFiltSize = 48;        % Background 생성 Filter 크기
    ROI_x = 1170;               % ROI 가로 (Pixels)
    ROI_y = 474;                % ROI 세로 (Pixels)
    panel_long_mm = 149.1;      % Panel 장축 Size(mm)
    division_y = 1;             % 등분 개수

    ActiveImage = importdata(fileName);

    % 회전
    ActiveImage = imrotate(double(ActiveImage),90);
    saveastiff(uint16(ActiveImage),[fileName(1:end-4) '_rotated.mim'])

    resize_V = size(ActiveImage,1);
    resize_H = size(ActiveImage,2);

    resize_V_dividied = floor(resize_V / division_y);

    for j = 1:division_y

        s = s+1;

        ActiveImage_divided = ActiveImage(1+(j-1)*floor(size(ActiveImage,1)/division_y):j*floor(size(ActiveImage,1)/division_y),:);
        saveastiff(uint16(ActiveImage_divided),[fileName(1:end-4) '_' num2str(j) '.mim'])

        % noise 제거
        hA = fspecial('average',[avgFiltSize, avgFiltSize]);
        ActiveImage_avg = imfilter(ActiveImage_divided,hA,'symmetric');
        saveastiff(uint16(ActiveImage_avg),[fileName(1:end-4) '_' num2str(j) '_avg10.mim'])

        % Background
        hA_ref = fspecial('average',[avgRefFiltSize, avgRefFiltSize]);
        ActiveImage_ref = imfilter(ActiveImage_divided,hA_ref,'symmetric');
        saveastiff(uint16(ActiveImage_ref),[fileName(1:end-4) '_' num2str(j) '_BG.mim'])

        center_x = round(resize_H/2);
        center_y = round(resize_V_dividied/2);
        start_x = floor(center_x-ROI_x/2+1);
        end_x = floor(center_x+ROI_X/2);
        start_y = floor(center_y-ROI_y/2+1);
        end_y = floor(center_y+ROI_y/2);

        data(s,1) = start_x;
        data(s,2) = start_y;
        data(s,3) = end_x;
        data(s,4) = end_y;
        

        % noise 제거 Profile
        profile = mean(ActiveImage_avg(start_y:end_y,start_x:end_x));

        start_data = 6;
        end_data = start_data + size(profile,2) - 1;
        data(s,start_data:end_data) = profile;

        % Background Profile
        profile_ref = mean(ActiveImage_ref(start_y:end_y,start_x:end_x));

        start_data = end_data + 2;
        end_data = start_data + size(profile_ref,2) - 1;
        data(s,start_data:end_data) = profile_ref;

        % dL/L(%) Profile
        Dprofile = 100*(profile - profile_ref)./profile_ref;

        start_data = end_data + 2;
        end_data = start_data + size(Dprofile,2) - 1;
        data(s,start_data:end_data) = Dprofile;

        mmPP = panel_long_mm / resize_H;
        x_cpmm = (1:floor(ROI_x/2)-1)/(mmPP*ROI_x);
        
        profile_fft_temp0 = fft(Dprofile);
        profile_fft_temp = abs(profile_fft_temp0);

        % FFT Profile
        profile_fft = profile_fft_temp(2:floor(ROI_x/2));

        start_data = end_data + 2;
        end_data = start_data + size(profile_fft,2) - 1;
        data(s,start_data:end_data) = profile_fft;
        
        % 내림차순으로 정렬
        [peaks_FFT,locPeaks_FFT]=findpeaks(profile_fft, x_cpmm);
        [peaks_FFT_sorted, I] = sort(peaks_FFT,'descend');
        locPeaks_FFT_sorted = locPeaks_FFT(I);
        
        % FFT 1st to 5th Peaks Wavelength & Intensity
        peakFFT_mm = 1./locPeaks_FFT_sorted(1:5);
        peakFFT_intensity = peaks_FFT_sorted(1:5);

        start_data = end_data + 2;
        end_data = start_data + size(peakFFT_mm,2) - 1;
        data(s,start_data:end_data) = peakFFT_mm;

        start_data = end_data + 2;
        end_data = start_data + size(peakFFT_intensity,2) - 1;
        data(s,start_data:end_data) = peakFFT_intensity;

    end
end

