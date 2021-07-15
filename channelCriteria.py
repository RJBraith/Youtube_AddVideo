import numpy as np

class channelCriteria:
    def __init__(self, likeCount, viewCount):
        '''
        Giving the likeCount and viewCount lists, calculates the mean, standard deviation in order to standardize each list

        Calculates a score by:
            Summing the two standardized lists     
        Then calculates a threshold variable which is:
            The sum of the means of each standardized list     
        '''

        self.likeCount = likeCount
        self.lc_mean = np.mean(self.likeCount)
        self.lc_sdev = np.std(self.likeCount)
        self.lc_std = abs((self.likeCount - self.lc_mean) / self.lc_sdev)

        self.viewCount = viewCount
        self.vc_mean = np.mean(self.viewCount)
        self.vc_sdev = np.std(self.viewCount)
        self.vc_std = abs((self.viewCount - self.vc_mean) / self.vc_sdev)

        self.threshold = abs(np.mean(self.lc_std) + np.mean(self.vc_std))
        self.score = (self.lc_std + self.vc_std)

    def threshold(self):
        return self.threshold

    def score(self):
        return self.score