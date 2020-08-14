import tushare as ts
import time

if __name__ == "__main__":
    nums = [1,2,3,4]
    nums = sorted(nums)
    numsLen = len(nums)
    # print(nums[int(numsLen/2)])
    # print(nums[int(numsLen/2)-1])
    print((nums[int(numsLen/2)]+nums[int(numsLen/2)-1])/2)
