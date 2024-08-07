---
layout: post
title: "Summary about Face Recognition with OpenCV"
date: 2015-03-06
comments: true
categories: [home, algorithms, vision]
abstract: "Summary about Face Recognition with OpenCV"
---

#### Some ideas and approachments about Face Recognition

#### geometric feature

-   marker points ( position of eyes, ears, noses, ...) are used to build the feature vector (the distance, the angle, ...)

#### Eigenfaces

-   The idea is that a facial image is a point from a high-dim image space, and a high-dim dataset is often described by correlated variables and therefore only a few meaningful dim account for most of the information .

-   alg

    -   [PCA](http://en.wikipedia.org/wiki/Eigenface/) alg finds the lower-dim subspace with maximum variance (with the mean) in data. ( that is, to turn a set of possibly correlated variables into a smaller set of uncorrelated variables) .

    -   There is a TRICK here in computing the eigenvectors: a M x N matrix (M rows, N columns) with M > N can only have N - 1 non-zero eigenvalues, so we can take the eigenvalue decomposition S of size N x N instead .

    -   The approach maximizes the total scatter, but if the variance is generated by an external source like light, components with a maximum variance over all classes aren't nessarily useful for classification.

-   The [API](http://docs.opencv.org/trunk/modules/contrib/doc/facerec/facerec_api.html) in OpenCV:

    -   Ptr<FaceRecognizer> createEigenFaceRecognizer(int num_components, double threshold)
        (~\sources\modules\contrib\src\facerec.cpp)

        -   Perform the PCA
        -   (~\modules\core\src\matmul.cpp)
            pca(data, Mat(), CV_PCA_DATA_AS_ROW, \_num_components)

            The parameter _num_components_ means that how many principal components to retain (it is not larger than the number of training samples) .

        -   Get the feature vectors (y here is the principal component )
            Mat y = subspaceProject(\_eigenvectors, \_mean, data.row(sampleIdx)

            The parameter _threshold_ here gives a upper distance limit in the prediction (It is the parameter _minDist_ in the Eigenfaces::predict())

            Eigenfaces::predict(InputArray \_src, int &minClass, double &minDist)

            Each test sample is projected into PCA subspace,and get the related label based on the NORM_L2 distance in the trained subspace.

#### Fisherfaces

#### Local Binary Patterns Histograms (LBPH)

-   idea

    -   The focus is only on extracting local features of an object, thus the features in this waywill have a low-dim implicitly.

    -   Also, the local description has to be a bit robust against image illumination variations (things like scale,translation or rotation), so the Local Binary Patterns (LBP) is given to summarize the local structure in a image by comparing each pixel with its neighborhood .

-   The [API](http://docs.opencv.org/trunk/modules/contrib/doc/facerec/facerec_api.html) in OpenCV Ptr<FaceRecognizer> createLBPHFaceRecognizer(int radius,int neighbors, int grid_x, int grid_y, double threshold) Calculate lbp image

    -   elbp(src[sampleIdx],\_radius,\_neighbors)

        -   The parameters _radius_ and _neighbors_ are used in the local binary pattern creation

    -   Get spatial histogram from this lbp image

```c++
      Mat p = spatial_histogram(
                lbp_image, /* lbp_image */
                /* number of possible patterns */
                static_cast<int>(std::pow(2.0, static_cast<double>(_neighbors))),
                _grid_x, /* grid size x */
                _grid_y, /* grid size y */
                true)
```

      The parameters *gird_x* and *grid_y* control the grid size of the spatial histograms.
              At last the feature vectors (p here is the spatial histogram) are given .

      LBPH::predict(InputArray _src, int &minClass, double &minDist)

      compareHist(_histograms[sampleIdx], query, CV_COMP_CHISQR)

      Chi-square test is used for the distance measure

#### The Performance

-   Receiver operating characteristic ([ROC](http://en.wikipedia.org/wiki/Receiver_operating_characteristic))

    -   A ROC space is defined by TAR (I.e., the rate of genuine attempts accepted) and FAR(I.e., the rate of impostor attempts accepted) as y and x axes respectively, which depicts relative trade-offs between true positive (benefits) and false positive (costs).

-   Cumulative Match Characteristic (CMC)
    -   It plots the probability of identification against the returned 1:N candidate list size. It shows the probability that a given user appears in different sized candidate lists.

#### Reference

-   [Face Recognition with OpenCV](http://docs.opencv.org/2.4/modules/contrib/doc/facerec/facerec_tutorial.html)
-   [Eigenface](http://en.wikipedia.org/wiki/Eigenface/)
-   [FaceRecognizer API](http://docs.opencv.org/trunk/modules/contrib/doc/facerec/facerec_api.html)
-   [ROC](http://en.wikipedia.org/wiki/Receiver_operating_characteristic)
