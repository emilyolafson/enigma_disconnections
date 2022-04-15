
%% flip all subjects with L lesions to the R
df=readtable('~/GIT/ENIGMA/data/Behaviour_Information_ALL_April7_2022_sorted.csv')

%df=df(~isnan(df.CHRONICITY),:)
%df=df(~isnan(df.SEX),:)
%df=df(~isnan(df.AGE),:)
%df=df(~isnan(df.LESIONED_HEMISPHERE),:)
%df=df(~isnan(df.NORMED_MOTOR),:)

%df=df(df.CHRONICITY==180,:)

histogram(df.DAYS_POST_STROKE)
title('Days post stroke')

mean(df.DAYS_POST_STROKE, 'omitnan')
sum(isnan(df.DAYS_POST_STROKE))

max(df.DAYS_POST_STROKE)

sub_left=df.LESIONED_HEMISPHERE==1 % to flip
sub_left=df.BIDS_ID(logical(sub_left))

counter=0
for i=1:size(df,1) %copy everything to say flipped
    counter=counter+1
    [status, cmdout]=system(sprintf('cp %s* %s', ['/Users/emilyolafson/GIT/ENIGMA/data/lesionmasks/2mm/', cell2mat(df.BIDS_ID(i))], ['/Users/emilyolafson/GIT/ENIGMA/data/lesionmasks/2mm/', cell2mat(df.BIDS_ID(i)), '_flipped.nii.gz'] ));
end

% get sagittal midcoordinate and determine whether it's on the L or R side.
cstatlas=read_avw('/usr/local/fsl/data/atlases/JHU/JHU-ICBM-tracts-prob-2mm.nii.gz');
Rcst=squeeze(cstatlas(:,:,:,3));
Rcst=double(Rcst)

% midsagittal plane: x = 45
% 0:44 = right
% 46:91 = left
for i=1:109
    imagesc(squeeze(Rcst(i,:,:)))
    title(['i = ', num2str(i)])
    drawnow
    pause(0.3)
    hold on
end



addpath('/usr/local/fsl/')
counter=0

for i=1:size(sub_left,1) %copy everything to say flipped
    counter=counter+1
    [status, cmdout]=system(sprintf('/usr/local/fsl/bin/fslswapdim %s -x y z %s', ['/Users/emilyolafson/GIT/ENIGMA/data/lesionmasks/2mm/', cell2mat(sub_left(i)), '_flipped.nii.gz'], ['/Users/emilyolafson/GIT/ENIGMA/data/lesionmasks/2mm/', cell2mat(sub_left(i)), '_flipped.nii.gz'] ));
end