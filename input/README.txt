about input:
dataset is currently gopro-imu dataset: playground 3
the intended items to be recognized are: bicycle, bench 

to convert video to image sequence:
avconv -i video.mp4 -f image2 frame%00d.jpg

input specs:
fps = same as video, 29.97 
frame interval = 480 - 550

TODO: 
write to two output files, and compare 
test with the iou model
figure out how to change from imu frame to camera frame  
