import backtrader as bt


# 创建策略类
class MAStrategy(bt.Strategy):
    params = (
        ("ma_short", 5),  # 短期均线周期
        ("ma_long", 20),  # 长期均线周期
    )

    def __init__(self):
        # 定义均线指标
        self.ma_short = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.ma_short, plotname="MA5"
        )
        self.ma_long = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.ma_long, plotname="MA20"
        )

    def next(self):
        # 如果短期均线向上穿过长期均线，买入信号
        if self.ma_short[0] > self.ma_long[0] and self.ma_short[-1] <= self.ma_long[-1]:
            self.buy(size=1)
        # 如果短期均线向下穿过长期均线，卖出信号
        elif self.ma_short[0] < self.ma_long[0] and self.ma_short[-1] >= self.ma_long[-1]:
            self.sell(size=1)


# 创建回测函数
def run_backtest(datafile):
    # 初始化 Backtrader 引擎
    cerebro = bt.Cerebro()

    # 加载数据
    data = bt.feeds.GenericCSVData(
        dataname=datafile,
        dtformat="%Y-%m-%d %H:%M:%S",  # 日期时间格式，精确到分钟
        timeframe=bt.TimeFrame.Minutes,  # 时间间隔为分钟
        compression=1,  # 每分钟一条数据
        openinterest=-1,  # 无持仓信息
        headers=True,  # 数据包含列名
        separator=",",  # 使用逗号分隔
        open=1,  # 数据第 2 列是 open
        high=3,  # 数据第 4 列是 high
        low=4,  # 数据第 5 列是 low
        close=2,  # 数据第 3 列是 close
        volume=5  # 数据第 6 列是 volume
    )
    cerebro.adddata(data)

    # 添加策略
    cerebro.addstrategy(MAStrategy)

    # 设置初始资金
    cerebro.broker.set_cash(10000)

    # 设置佣金
    cerebro.broker.setcommission(commission=0.001)

    # 设置每股买入量
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)

    # 运行回测
    print("初始资金: %.2f" % cerebro.broker.getvalue())
    cerebro.run()
    print("回测结束后资金: %.2f" % cerebro.broker.getvalue())

    # 绘制结果
    cerebro.plot()


# 执行回测
datafile = r'../data/btc_data_with_datetime.csv'  # 替换为你的数据文件路径
run_backtest(datafile)
