import pandas as pd
import copy


class ChipDistribution:

    def __init__(self):
        self.data = None
        self.chip = {}  # 当前获利盘
        self.chip_list = {}  # 所有的获利盘的

    def get_data(self):
        self.data = pd.read_csv('test.csv')

    def calc_jun(self, date_t, high_t, low_t, vol_t, turnover_rate_t, a, min_d):

        x = []
        l = (high_t - low_t) / min_d
        for i in range(int(l)):
            x.append(round(low_t + i * min_d, 2))
        length = len(x)
        each_v = vol_t / length
        for i in self.chip:
            self.chip[i] = self.chip[i] * (1 - turnover_rate_t * a)
        for i in x:
            if i in self.chip:
                self.chip[i] += each_v * (turnover_rate_t * a)
            else:
                self.chip[i] = each_v * (turnover_rate_t * a)
        import copy
        self.chip_list[date_t] = copy.deepcopy(self.chip)

    def calcuSin(self, date_t, high_t, low_t, avg_t, vol_t, turnover_rate_t, min_d, a):
        x = []

        l = (high_t - low_t) / min_d
        for i in range(int(l)):
            x.append(round(low_t + i * min_d, 2))

        length = len(x)

        # 计算仅仅今日的筹码分布
        tmpChip = {}
        eachV = vol_t / length

        # 极限法分割去逼近
        for i in x:
            x1 = i
            x2 = i + min_d
            h = 2 / (high_t - low_t)
            s = 0
            if i < avg_t:
                y1 = h / (avg_t - low_t) * (x1 - low_t)
                y2 = h / (avg_t - low_t) * (x2 - low_t)
                s = min_d * (y1 + y2) / 2
                s = s * vol_t
            else:
                y1 = h / (high_t - avg_t) * (high_t - x1)
                y2 = h / (high_t - avg_t) * (high_t - x2)

                s = min_d * (y1 + y2) / 2
                s = s * vol_t
            tmpChip[i] = s

        for i in self.chip:
            self.chip[i] = self.chip[i] * (1 - turnover_rate_t * a)

        for i in tmpChip:
            if i in self.chip:
                self.chip[i] += tmpChip[i] * (turnover_rate_t * a)
            else:
                self.chip[i] = tmpChip[i] * (turnover_rate_t * a)
        import copy
        self.chip_list[date_t] = copy.deepcopy(self.chip)

    def calcu(self, date_t, high_t, low_t, avg_t, vol_t, turnover_rate_t, min_d=0.01, flag=1, ac=1):
        if flag == 1:
            self.calcuSin(date_t, high_t, low_t, avg_t, vol_t, turnover_rate_t, a=ac, min_d=min_d)
        elif flag == 2:
            self.calc_jun(date_t, high_t, low_t, vol_t, turnover_rate_t, a=ac, min_d=min_d)

    def calc_chip(self, flag=1, ac=1):  # flag 使用哪个计算方式,    AC 衰减系数
        low = self.data['low']
        high = self.data['high']
        vol = self.data['volume']
        turnover_rate = self.data['TurnoverRate']
        avg = self.data['avg']
        date = self.data['date']

        for i in range(len(date)):
            #     if i < 90:
            #         continue

            high_t = high[i]
            low_t = low[i]
            vol_t = vol[i]
            turnover_rate_t = turnover_rate[i]
            avg_t = avg[i]
            # print(date[i])
            date_t = date[i]
            self.calcu(date_t, high_t, low_t, avg_t, vol_t, turnover_rate_t / 100, flag=flag,
                       ac=ac)  # 东方财富的小数位要注意，兄弟萌。我不除100懵逼了

        # 计算winner

    def winner(self, p=None):
        profit = []
        date = self.data['date']

        if p is None:  # 不输入默认close
            p = self.data['close']
            count = 0
            for i in self.chip_list:
                # 计算目前的比例

                chip = self.chip_list[i]
                total = 0
                be = 0
                for c in chip:
                    total += chip[c]
                    if c < p[count]:
                        be += chip[c]
                if total != 0:
                    bili = be / total
                else:
                    bili = 0
                count += 1
                profit.append(bili)
        else:
            for i in self.chip_list:
                # 计算目前的比例

                chip = self.chip_list[i]
                total = 0
                be = 0
                for c in chip:
                    total += chip[c]
                    if c < p:
                        be += chip[c]
                if total != 0:
                    bili = be / total
                else:
                    bili = 0
                profit.append(bili)

        # import matplotlib.pyplot as plt
        # plt.plot(date[len(date) - 200:-1], Profit[len(date) - 200:-1])
        # plt.show()

        return profit

    def l_winner(self, n=5, p=None):
        data = copy.deepcopy(self.data)
        date = data['date']
        ans = []
        for i in range(len(date)):
            print(date[i])
            if i < n:
                ans.append(None)
                continue
            self.data = data[i - n:i]
            self.data.index = range(0, n)
            self.__init__()
            self.calc_chip()  # 使用默认计算方式
            a = self.winner(p)
            ans.append(a[-1])
        import matplotlib.pyplot as plt
        plt.plot(date[len(date) - 60:-1], ans[len(date) - 60:-1])
        plt.show()

        self.data = data
        return ans

    def cost(self, n):
        date = self.data['date']
        n = n / 100  # 转换成百分比
        ans = []
        for i in self.chip_list:  # 我的chip_list本身就是有顺序的
            chip = self.chip_list[i]
            chip_key = sorted(chip.keys())  # 排序
            total = 0  # 当前比例
            sum_of = 0  # 所有筹码的总和
            for j in chip:
                sum_of += chip[j]

            for j in chip_key:
                tmp = chip[j]
                tmp = tmp / sum_of
                total += tmp
                if total > n:
                    ans.append(j)
                    break
        import matplotlib.pyplot as plt
        plt.plot(date[len(date) - 1000:-1], ans[len(date) - 1000:-1])
        plt.show()
        return ans


if __name__ == "__main__":
    cd = ChipDistribution()
    cd.get_data()  # 获取数据
    cd.calc_chip(flag=1, ac=1)  # 计算
    cd.winner()  # 获利盘
    cd.cost(90)  # 成本分布

    cd.l_winner()
