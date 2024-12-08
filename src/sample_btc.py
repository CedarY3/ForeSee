import datetime
import backtrader as bt


# 创建策略继承bt.Strategy
class TestStrategy(bt.Strategy):
    def __init__(self):
        self.summary = {
            'total_trades': 0,
            'total_commission': 0,
        }
        # 保存收盘价的引用
        self.dataclose = self.datas[0].close
        # 跟踪挂单
        self.order = None
        # 买入价格和手续费
        self.buyprice = None
        self.buycomm = None

        # 绘制图形时候用到的指标
        # bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        # bt.indicators.WeightedMovingAverage(self.datas[0], period=25,subplot=True)
        # bt.indicators.MACDHisto(self.datas[0])
        # rsi = bt.indicators.RSI(self.datas[0])
        # bt.indicators.SmoothedMovingAverage(rsi, period=10)
        # bt.indicators.ATR(self.datas[0], plot=False)

        # 定义均线指标
        self.ma_x = bt.indicators.SimpleMovingAverage(
            self.data.close,
            period=5,
            plotname="MA5"
        )

    def buy_sig(self):  # 买入信号定义函数
        return (self.ma_x[-1] < self.datas[0].close[-1]) and (self.datas[0].close[0] <= self.ma_x[0])

    def sell_sig(self):  # 卖出信号定义函数
        return (self.ma_x[-1] >= self.datas[0].close[-1]) and (self.datas[0].close[0] > self.ma_x[0])


    def log(self, txt, dt=None):
        # 记录策略的执行日志
        dt = dt or self.datas[0].datetime.datetime(0)
        # print('%s, %s' % (dt.isoformat(), txt))

    # 订单状态通知，买入卖出都是下单
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '已买入, 价格: %.6f, 费用: %.6f, 佣金 %.6f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.summary['total_commission'] += order.executed.comm
            elif order.issell():
                self.log('已卖出, 价格: %.6f, 费用: %.6f, 佣金 %.6f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                self.summary['total_trades'] += 1
                self.summary['total_commission'] += order.executed.comm
            # 记录当前交易数量
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        # 其他状态记录为：无挂起订单
        self.order = None

    # 交易状态通知，一买一卖算交易
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易利润, 毛利润 %.6f, 净利润 %.6f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        # 记录收盘价
        # self.log('Close, %.6f' % self.dataclose[0])
        # 如果有订单正在挂起，不操作
        if self.order:
            return

        # 如果没有持仓则买入
        if not self.position:
            # 买入信号
            if self.buy_sig():
                # 买入
                self.log('买入单, %.6f' % self.dataclose[0])
                # 跟踪订单避免重复
                self.order = self.buy()
        else:
            # 卖出信号
            if self.sell_sig():
                # 全部卖出
                self.log('卖出单, %.6f' % self.dataclose[0])
                # 跟踪订单避免重复
                self.order = self.sell()


datafile = r'../data/btc_data_2023.csv'  # 替换为你的数据文件路径
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
    volume=5,  # 数据第 6 列是 volume
    # fromdate=datetime.datetime(2024, 11, 18),
    # todate=datetime.datetime(2024, 11, 20),
)

# 创建Cerebra引擎
cerebra = bt.Cerebro()
# 为Cerebra引擎添加策略
cerebra.addstrategy(TestStrategy)

# 加载交易数据
cerebra.adddata(data)
# 设置投资金额1000.0
cerebra.broker.setcash(10000.0)
# 每笔交易使用固定交易量
cerebra.addsizer(bt.sizers.FixedSize, stake=0.001)
# 设置佣金为0.0
cerebra.broker.setcommission(commission=0.0005)
# 引擎运行前打印期出资金
print('组合期初资金: %.6f' % cerebra.broker.getvalue())
results = cerebra.run()
# 引擎运行后打期末资金
print('组合期末资金: %.6f' % cerebra.broker.getvalue())
# 绘制图像
print(results[0].summary['total_commission'])
print(results[0].summary['total_trades'])
cerebra.plot()
