Yuki
----
Yuki is a stand-alone program written using the 
[FBS](https://www.learnpyqt.com/courses/packaging-and-distribution/packaging-pyqt5-apps-fbs/) 
framework that can help the producer analyze the information in the video and 
output it as an excel file.

![icon](https://github.com/loonghao/Yuki/blob/master/src/yuki/resources/images/yuki.png)

Features
========
- Analyze videos.
- Export thumbnails.
- Save to ExcelWriter.

Requirements
============
- fbs==0.8.6
- PySide2==5.12.2
- XlsxWriter==1.0.2

![demo](https://user-images.githubusercontent.com/13111745/44737904-d0cc7500-ab25-11e8-8a71-dccb574b777f.gif)

Build exe and installer via fbs
===============================

```shell script
fbs freeze
```
```shell script
fns installer
```
More details docs about [`fbs`](https://build-system.fman.io/manual/)

