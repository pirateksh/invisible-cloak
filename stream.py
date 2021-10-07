# Import libraries

import numpy as np
import cv2 as cv
import argparse
import time

HSV_Ranges = {'red': [[[0, 120, 70], [10, 255, 255]], [[161, 155, 84], [179, 255, 255]]],
              'blue': [[94, 80, 2], [126, 255, 255]],
              'green': [[25, 52, 72], [102, 255, 255]]}


def get_arguments():
    """
    Funtion to extract the arguments from the command line and 
    provide description for the options available for this script
    """
    ap = argparse.ArgumentParser(
        description='Python script to hide the content behind the cloak of given color')
    ap.add_argument('-c', '--color', required=True,
                    help='Color of cloak to hide: red, blue, green')
    args = vars(ap.parse_args())
    # print(args)
    if not args['color'].upper() in ['RED', 'BLUE', 'GREEN']:
        ap.error("Please speciy a correct color from given options: red, blue, green")

    return args


def invisible_cloak():

    args = get_arguments()
    """
        Creating a video capture object
        Constructors - 
        Video address: To run code on any video.
        Webcam number: To run code based on webcam video.
            (Here 0, as we have only one webcam).

        This object just specifies the video OR which webcam
        will be used to record video(this doesn't start camera).
    """
    cap = cv.VideoCapture(0)

    # To give camera time to capture the background initially.
    time.sleep(2)

    """
        This variable will store background image that will be
        displayed when cloak is used.
    """
    background = 0

    for i in range(30):
        """
            We are reading the input here using video capture object.
            We are giving 30 iterations to capture the background
            initially.
            cap.read() returns - image that is capture 
                and return value(True, If OK otherwise False).
        """
        ret, background = cap.read()

    while(cap.isOpened()):
        """
            This while loop will execute till capture object
            is open OR it is running.
            In other words it means - when webcam is capturing me,
                do following...
        """

        # Capturing image again (to perform operation on it)
        ret, img = cap.read()

        if not ret:
            """
                Terminating condition - 
                When webcam is closed, ret = False
            """
            break

        """
            Color space of image when it is captured.
            Webcame by default captures in BGR colour space.
            Some other color spaces are - RGB, Gray, YCrCb, etc.
            RGB - Linear combination of Red, Blue and Green.
            YCrCb - Y (luminescence), Cr and Cb are certain ranges.

            HSV/HSB- Hue Saturation Value/Brightness.
        """

        # Converting image from BGR -> HSV nad storing it.
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

        """
            In HSV, there is a disk and color is distributed according to angle,
            i.e. from 0 - 360. But, in OpenCV, color is stored in 8 bits, 
            i.e. we can store value till 0 to 2^8 - 1 = 255 only.
            So, The size of disk is reduces to  180 degrees and Hue value is 
            increased to twice.
            Normal Hue Range (in degree):
            Red: 0 - 60
            Yellow: 61 - 120
            Green: 121 - 180
            Cyan: 181 - 240
            Blue: 241 - 300
            Magenta: 301 - 360

            Here, if we are using RED cloth, we can use range 0 - 30, 
            but we will use 0 - 10(as after 10 the color will be very light) and 170 - 180
            for RED color.
            
            [0, 120, 70] are H S V values where, H=0, S=120, V=70.
            Saturation - It tells about darkness.

            In lower limit of red, i.e. lower_red, We are using H=120 and B=70,
            as below that the saturation and brightness will be very code will also
            operate on pinkish colors while we want it to operate on RED only.
        """
        mask1 = 0
        """
            Input is hsv - video frame captured by camera.
            We will check whether there is any region having HSB values
            b/w lower_red and upper_red in captured hsv video frame.
            
            inRange() - This is separating the cloak part(here).
        """

        # If color is red then it will have 2 ranges from 0-10 and 170 -180
        if args['color'].upper() == 'RED':
            # Lower limit of H, S and B
            first_lower_red = np.array(HSV_Ranges[args['color']][0][0])
            # Upper Limit of H, S and B
            first_upper_red = np.array(HSV_Ranges[args['color']][0][1])
            mask1 = cv.inRange(hsv, second_lower_red, second_upper_red)

            # Repeating with 170-180 degree
            second_lower_red = np.array(HSV_Ranges[args['color']][1][0])
            second_upper_red = np.array(HSV_Ranges[args['color']][1][1])
            mask2 = cv.inRange(hsv, first_lower_red, first_upper_red)

            # Overloading + operator for Bitwise OR.
            mask1 = mask1 + mask2
        else:
            lower_range = np.array(HSV_Ranges[args['color']][0])
            upper_range = np.array(HSV_Ranges[args['color']][1])
            mask1 = cv.inRange(hsv, lower_range, upper_range)

        """
            Used for morphological transformations.
            MORPH_OPEN: Removes noise from image.
            @param: input image, cv.MORPH_OPEN, kernel
            kernel: It is a filter
            np.ones(3, 3): Creates a matrix of 3 X 3 with all ones and 
                multiplies it with pixel matrix of image over 2 iterations(as specified).

            MORPH_DILATE: Improves smoothness of image.

            Note: These operations are normally done on Black and White image, but here
                we are doing them on HSV coloured space.
        """

        mask1 = cv.morphologyEx(mask1, cv.MORPH_OPEN,
                                np.ones((3, 3), np.uint8), iterations=2)

        mask1 = cv.morphologyEx(mask1, cv.MORPH_DILATE,
                                np.ones((3, 3), np.uint8), iterations=1)

        """
            Opposite of mask1 i.e. everything except the cloak, rest of the background.
            (mask1 was cloak).
        """
        mask2 = cv.bitwise_not(mask1)

        """
            res1: Bitwise and b/w background and mask1.
            This is used for segmentation of the colour i.e. we are differentiating cloak color
            form rest of the background.

            res2: Bitwise and b/w img and mask2.
            This is used to substitute the cloak part.

            background: Image which is to be displayed when cloak is in frame.
            img: Image captured by camera.
        """
        res1 = cv.bitwise_and(background, background, mask=mask1)
        res2 = cv.bitwise_and(img, img, mask=mask2)

        """
            We are linearly adding two images using addWeighted() function.
            Following equation is generated:
            alpha * source image 1 + beta * source image 2 + gamma = 0

            Here, alpha = beta = 1 and gamma = 0.
        """
        final_output = cv.addWeighted(res1, 1, res2, 1, 0)

        # Displays final image
        cv.imshow("Invisible Cloak", final_output)

        """
            On pressing ESC key, window will shut down and program execution will stop.
        """
        k = cv.waitKey(10)

        if k == 27:
            break

    # Destructing video capture object.
    cap.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    invisible_cloak()
