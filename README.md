# Activity Recognition
Action Recognition Deep Learning Project

### Requirements

`pip install -r requirements.txt`

### Arguments

- `"m", "--model" :` path to trained serialized model
- `"-l", "--label-bin":` path to  label binarizer
- `"-i", "--input":` path to our input video (e.g. `example_clips/video.mp4`)
- `"-o", "--output":` path to our output video (e.g. `output/myVideo.avi`)
- `"-s", "--size":` size of queue for averaging (e.g. 128)
- `"-a", "--action":` choose a predictive action from this list (`drinking, cooking`). This name will be used in labeling the JSON file and the output figure y_label.
***

### Instruction Video: [LINK](https://youtu.be/Dvp9Gt67u_0)

***

### Run

- Create three folders: **model**, **output** and **example_clips** 
- Before running the code, download the *pre-trained Model* and the *binarized Labels* from this [>>link<<](https://drive.google.com/drive/folders/14ly0meHnHMOCxciVzblcNhQsX0fD_aaP?usp=sharing) and add it to the *model* folder.
- Create an empty folder called `output` for the code output.
- Create a folder called `example_clips` and put your test videos in it.

`python predict_video.py --model model/activity.model --label-bin model/lb.pickle --input` **YOUR VIDEO PATH** `--output output/`**ARBITRARY NAME**`.avi --action` **drinking/cooking** `--size 128`

***

### Project IV

- Report: 
1. [drinking](https://drive.google.com/file/d/1YqWGvZUGXuv7tw1MbpSnm9rByBTuu8Ob/view?usp=sharing)
2. [cooking](https://drive.google.com/file/d/1vGiTdP4TwbFTYxhbpMdxjYWJG0ZPDahq/view?usp=sharing)

|Drinking Video Samples                |Cooking Video Samples                |
|:------------------------------------:|:-----------------------------------:|
|[drink1](https://youtu.be/epeNAmsSaT8)|[cook1](https://youtu.be/fcBFr5MDm-Y)|
|[drink2](https://youtu.be/Me9ukITLTfk)|[cook2](https://youtu.be/oiKxjYLTDHA)|
|[drink3](https://youtu.be/E8W2hXuCivw)|[cook3](https://youtu.be/0Cac3yVfR7E)|
|[drink4](https://youtu.be/JCjt7vHeY_U)|[cook4](https://youtu.be/jElkBPTWpSU)|
|[drink5](https://youtu.be/LGWF0j00oMI)|[cook5](https://youtu.be/2DGt6KwJVSQ)|

***

### Project V

|Drinking Video Samples                |Cooking Video Samples                |
|:------------------------------------:|:-----------------------------------:|
|[drink1](https://youtu.be/epeNAmsSaT8)|[cook1](https://youtu.be/fcBFr5MDm-Y)|
|[drink2](https://youtu.be/Me9ukITLTfk)|[cook2](https://youtu.be/oiKxjYLTDHA)|
|[drink3](https://youtu.be/E8W2hXuCivw)|[cook3](https://youtu.be/0Cac3yVfR7E)|
|[drink4](https://youtu.be/JCjt7vHeY_U)|[cook4](https://youtu.be/jElkBPTWpSU)|
|[drink5](https://youtu.be/LGWF0j00oMI)|[cook5](https://youtu.be/2DGt6KwJVSQ)|

***


