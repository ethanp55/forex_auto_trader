import pandas as pd
import numpy as np
import math
import talib
from tensorflow.keras.layers import GRU, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras.models import load_model, Sequential
from collections import deque
from sklearn.preprocessing import StandardScaler
from pickle import dump, load

# ----------------------------------------------------------------------------------------------------------------------
file_path = '/content/drive/My Drive/Forex_Robot/'

# ----------------------------------------------------------------------------------------------------------------------
df = pd.read_csv(file_path + 'Oanda_Eur_Usd_M30.csv')
df.Date = pd.to_datetime(df.Date, format='%Y.%m.%d %H:%M:%S.%f')
df = df.iloc[50000:, :]
df.reset_index(drop=True, inplace=True)

df

# ----------------------------------------------------------------------------------------------------------------------
# Add hour of day, day of week, and month of year (for additional features)
# Use sine and cosine to keep the cyclic nature of hour, day, and month
#  (December is closer to January than October, midnight is closer to 1 am than
#  10 pm, etc.)
df['sin_hour'] = np.sin(2 * np.pi * df['Date'].dt.hour / 24)
df['cos_hour'] = np.cos(2 * np.pi * df['Date'].dt.hour / 24)
df['sin_day'] = np.sin(2 * np.pi * df['Date'].dt.day / 7)
df['cos_day'] = np.cos(2 * np.pi * df['Date'].dt.day / 7)
df['sin_month'] = np.sin(2 * np.pi * df['Date'].dt.month / 12)
df['cos_month'] = np.cos(2 * np.pi * df['Date'].dt.month / 12)

# Plots to illustrate cyclic nature of time
df.sin_month.plot()
df.cos_month.plot()

# Show the updated dataframe
df.head()

# ----------------------------------------------------------------------------------------------------------------------
# Add technical indicators (for additional features)
# Bid technical indicators
# df['Bid_MACD'], df['Bid_MACD_Signal'], df['Bid_MACD_hist'] = talib.MACD(df['Bid_Close'])
# df['Bid_EMA200'] = talib.EMA(df['Bid_Close'], timeperiod=200)
# df['Ask_MACD'], df['Ask_MACD_Signal'], df['Ask_MACD_hist'] = talib.MACD(df['Ask_Close'])
# df['Ask_EMA200'] = talib.EMA(df['Ask_Close'], timeperiod=200)


df['Bid_SMA1'] = talib.SMA(df['Bid_Close'], timeperiod=10)
df['Bid_SMA1_Envelope_Upper'] = df['Bid_SMA1'] + (0.1 * df['Bid_SMA1'])
df['Bid_SMA1_Envelope_Lower'] = df['Bid_SMA1'] - (0.1 * df['Bid_SMA1'])
df['Bid_EMA1'] = talib.EMA(df['Bid_Close'], timeperiod=10)
df['Bid_EMA1_Envelope_Upper'] = df['Bid_EMA1'] + (0.1 * df['Bid_EMA1'])
df['Bid_EMA1_Envelope_Lower'] = df['Bid_EMA1'] - (0.1 * df['Bid_EMA1'])
df['Bid_SMA2'] = talib.SMA(df['Bid_Close'], timeperiod=20)
df['Bid_SMA2_Envelope_Upper'] = df['Bid_SMA2'] + (0.1 * df['Bid_SMA2'])
df['Bid_SMA2_Envelope_Lower'] = df['Bid_SMA2'] - (0.1 * df['Bid_SMA2'])
df['Bid_EMA2'] = talib.EMA(df['Bid_Close'], timeperiod=20)
df['Bid_EMA2_Envelope_Upper'] = df['Bid_EMA2'] + (0.1 * df['Bid_EMA2'])
df['Bid_EMA2_Envelope_Lower'] = df['Bid_EMA2'] - (0.1 * df['Bid_EMA2'])
df['Bid_SMA3'] = talib.SMA(df['Bid_Close'], timeperiod=30)
df['Bid_SMA3_Envelope_Upper'] = df['Bid_SMA3'] + (0.1 * df['Bid_SMA3'])
df['Bid_SMA3_Envelope_Lower'] = df['Bid_SMA3'] - (0.1 * df['Bid_SMA3'])
df['Bid_EMA3'] = talib.EMA(df['Bid_Close'], timeperiod=30)
df['Bid_EMA3_Envelope_Upper'] = df['Bid_EMA3'] + (0.1 * df['Bid_EMA3'])
df['Bid_EMA3_Envelope_Lower'] = df['Bid_EMA3'] - (0.1 * df['Bid_EMA3'])
df['Bid_BB_Upper_Band'], df['Bid_BB_Middle_Band'], df['Bid_BB_Lower_Band'] = talib.BBANDS(
    df['Bid_Close'], timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
df['Bid_MACD'], df['Bid_MACD_Signal'], df['Bid_MACD_hist'] = talib.MACD(df['Bid_Close'],
                                                            fastperiod=12,
                                                            slowperiod=26,
                                                            signalperiod=9)
df['Bid_Parabollic_SAR'] = talib.SAR(df['Bid_High'], df['Bid_Low'], acceleration=0, maximum=0)
df['Bid_Slowk'], df['Bid_Slowd'] = talib.STOCH(df['Bid_High'], df['Bid_Low'], df['Bid_Close'],
                                       fastk_period=5, slowk_period=3,
                                       slowk_matype=0, slowd_period=3,
                                       slowd_matype=0)
df['Bid_RSI'] = talib.RSI(df['Bid_Close'], timeperiod=14)
df['Bid_Williams_Percent_Range'] = talib.WILLR(df['Bid_High'], df['Bid_Low'], df['Bid_Close'],
                                           timeperiod=14)
df['Bid_ADX'] = talib.ADX(df['Bid_High'], df['Bid_Low'], df['Bid_Close'], timeperiod=14)
df['Bid_ADXR'] = talib.ADXR(df['Bid_High'], df['Bid_Low'], df['Bid_Close'], timeperiod=14)
df['Bid_MOM'] = talib.MOM(df['Bid_Close'], timeperiod=10)
df['Bid_BOP'] = talib.BOP(df['Bid_Open'], df['Bid_High'], df['Bid_Low'], df['Bid_Close'])
df['Bid_AROONOSC'] = talib.AROONOSC(df['Bid_High'], df['Bid_Low'], timeperiod=14)
df['Bid_ATR'] = talib.ATR(df['Bid_High'], df['Bid_Low'], df['Bid_Close'], timeperiod=14)

# Ask technical indicators
df['Ask_SMA1'] = talib.SMA(df['Ask_Close'], timeperiod=10)
df['Ask_SMA1_Envelope_Upper'] = df['Ask_SMA1'] + (0.1 * df['Ask_SMA1'])
df['Ask_SMA1_Envelope_Lower'] = df['Ask_SMA1'] - (0.1 * df['Ask_SMA1'])
df['Ask_EMA1'] = talib.EMA(df['Ask_Close'], timeperiod=10)
df['Ask_EMA1_Envelope_Upper'] = df['Ask_EMA1'] + (0.1 * df['Ask_EMA1'])
df['Ask_EMA1_Envelope_Lower'] = df['Ask_EMA1'] - (0.1 * df['Ask_EMA1'])
df['Ask_SMA2'] = talib.SMA(df['Ask_Close'], timeperiod=20)
df['Ask_SMA2_Envelope_Upper'] = df['Ask_SMA2'] + (0.1 * df['Ask_SMA2'])
df['Ask_SMA2_Envelope_Lower'] = df['Ask_SMA2'] - (0.1 * df['Ask_SMA2'])
df['Ask_EMA2'] = talib.EMA(df['Ask_Close'], timeperiod=20)
df['Ask_EMA2_Envelope_Upper'] = df['Ask_EMA2'] + (0.1 * df['Ask_EMA2'])
df['Ask_EMA2_Envelope_Lower'] = df['Ask_EMA2'] - (0.1 * df['Ask_EMA2'])
df['Ask_SMA3'] = talib.SMA(df['Ask_Close'], timeperiod=30)
df['Ask_SMA3_Envelope_Upper'] = df['Ask_SMA3'] + (0.1 * df['Ask_SMA3'])
df['Ask_SMA3_Envelope_Lower'] = df['Ask_SMA3'] - (0.1 * df['Ask_SMA3'])
df['Ask_EMA3'] = talib.EMA(df['Ask_Close'], timeperiod=30)
df['Ask_EMA3_Envelope_Upper'] = df['Ask_EMA3'] + (0.1 * df['Ask_EMA3'])
df['Ask_EMA3_Envelope_Lower'] = df['Ask_EMA3'] - (0.1 * df['Ask_EMA3'])
df['Ask_BB_Upper_Band'], df['Ask_BB_Middle_Band'], df['Ask_BB_Lower_Band'] = talib.BBANDS(
    df['Ask_Close'], timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
df['Ask_MACD'], df['Ask_MACD_Signal'], df['Ask_MACD_hist'] = talib.MACD(df['Ask_Close'],
                                                            fastperiod=12,
                                                            slowperiod=26,
                                                            signalperiod=9)
df['Ask_Parabollic_SAR'] = talib.SAR(df['Ask_High'], df['Ask_Low'], acceleration=0, maximum=0)
df['Ask_Slowk'], df['Ask_Slowd'] = talib.STOCH(df['Ask_High'], df['Ask_Low'], df['Ask_Close'],
                                       fastk_period=5, slowk_period=3,
                                       slowk_matype=0, slowd_period=3,
                                       slowd_matype=0)
df['Ask_RSI'] = talib.RSI(df['Ask_Close'], timeperiod=14)
df['Ask_Williams_Percent_Range'] = talib.WILLR(df['Ask_High'], df['Ask_Low'], df['Ask_Close'],
                                           timeperiod=14)
df['Ask_ADX'] = talib.ADX(df['Ask_High'], df['Ask_Low'], df['Ask_Close'], timeperiod=14)
df['Ask_ADXR'] = talib.ADXR(df['Ask_High'], df['Ask_Low'], df['Ask_Close'], timeperiod=14)
df['Ask_MOM'] = talib.MOM(df['Ask_Close'], timeperiod=10)
df['Ask_BOP'] = talib.BOP(df['Ask_Open'], df['Ask_High'], df['Ask_Low'], df['Ask_Close'])
df['Ask_AROONOSC'] = talib.AROONOSC(df['Ask_High'], df['Ask_Low'], timeperiod=14)
df['Ask_ATR'] = talib.ATR(df['Ask_High'], df['Ask_Low'], df['Ask_Close'], timeperiod=14)

df.dropna(inplace=True)
df.reset_index(drop=True, inplace=True)

# Store the original dates in a separate column - used in the trading environment
dates = df['Date']

# Drop the original date column (it is no longer needed)
df.drop('Date', axis=1, inplace=True)

df

# ----------------------------------------------------------------------------------------------------------------------
account_balance = 5000
percent_to_risk = 0.02
pips_to_risk = 30
n_units_per_trade = 10000
value_per_pip = n_units_per_trade * 0.0001

if ((value_per_pip * pips_to_risk) / account_balance) > percent_to_risk:
  print('To much money risked per trade -- change parameters')

pips_to_risk /= 10000

# ----------------------------------------------------------------------------------------------------------------------
def create_target(dataset, i, pred_period=4):
  curr_bid_open = dataset.loc[dataset.index[i], 'Bid_Open']
  curr_ask_open = dataset.loc[dataset.index[i], 'Ask_Open']
  sell_stop_loss = curr_bid_open + pips_to_risk
  sell_stop_gain = curr_bid_open - (1.5 * pips_to_risk)
  buy_stop_loss = curr_ask_open - pips_to_risk
  buy_stop_gain = curr_ask_open + (1.5 * pips_to_risk)
  tmp = i
  j = 0
  buy = False
  sell = False

  # Assume a buy
  while i < dataset.shape[0] and j < pred_period:
    curr_bid_high = dataset.loc[dataset.index[i], 'Bid_High']
    curr_bid_low = dataset.loc[dataset.index[i], 'Bid_Low']

    if curr_bid_low <= buy_stop_loss:
      break

    if curr_bid_high >= curr_ask_open + pips_to_risk:
      buy_stop_loss = curr_ask_open

    if curr_bid_high >= buy_stop_gain:
      buy = True
      break

    i += 1
    j += 1

  i = tmp
  j = 0

  # Assume a sell
  while i < dataset.shape[0] and j < pred_period:
    curr_ask_high = dataset.loc[dataset.index[i], 'Ask_High']
    curr_ask_low = dataset.loc[dataset.index[i], 'Ask_Low']

    if curr_ask_high >= sell_stop_loss:
      break

    if curr_ask_low <= curr_bid_open - pips_to_risk:
      sell_stop_loss = curr_bid_open

    if curr_ask_low <= sell_stop_gain:
      sell = True
      break

    i += 1
    j += 1

  if buy and sell:
    print('wtf')
    print(i)
    print()
    return 0

  elif buy:
    return 1

  elif sell:
    return 2

  else:
    return 0

# ----------------------------------------------------------------------------------------------------------------------
df['target'] = [create_target(df, i) for i in range(df.shape[0])]

# ----------------------------------------------------------------------------------------------------------------------
df['target'].value_counts()

# ----------------------------------------------------------------------------------------------------------------------
def get_sequential_data(input_df):
    sequential_data = []
    prev_data = deque(maxlen=60)

    for i in range(input_df.shape[0] - 1):
        row = input_df.iloc[i, :]
        prev_data.append([val for val in row[:-1]])

        if len(prev_data) == 60:
          target = input_df.iloc[i + 1, -1]
          sequential_data.append([np.array(prev_data), target])

    np.random.shuffle(sequential_data)

    no_actions = []
    buys = []
    sells = []

    for seq, target in sequential_data:
        if target == 0 :
          no_actions.append([seq, np.array([1, 0, 0])])

        elif target == 1:
          buys.append([seq, np.array([0, 1, 0])])

        elif target == 2:
          sells.append([seq, np.array([0, 0, 1])])

    np.random.shuffle(no_actions)
    np.random.shuffle(buys)
    np.random.shuffle(sells)

    lower = min(len(no_actions), len(buys), len(sells))

    no_actions = no_actions[:int(lower * 1.5)]
    # buys = buys[:lower]
    # sells = sells[:lower]

    sequential_data = no_actions + buys + sells
    np.random.shuffle(sequential_data)

    return sequential_data

# ----------------------------------------------------------------------------------------------------------------------
test_df = df.iloc[df.shape[0] - 7000:, :]
test_df.reset_index(drop=True, inplace=True)
df = df.iloc[0:df.shape[0] - 7000, :]
df.reset_index(drop=True, inplace=True)

# ----------------------------------------------------------------------------------------------------------------------
sequential_data = get_sequential_data(df)

# ----------------------------------------------------------------------------------------------------------------------
training_proportion = 0.7
train_test_cutoff_index = int(len(sequential_data) * training_proportion)

train_set = sequential_data[0:train_test_cutoff_index]
test_set = sequential_data[train_test_cutoff_index:]

print('Dataset shapes:')
print(len(train_set))
print(len(test_set))

# ----------------------------------------------------------------------------------------------------------------------
x_train = []
y_train = []

for seq, target in train_set:
  x_train.append(seq)
  y_train.append(target)

x_test = []
y_test = []

for seq, target in test_set:
  x_test.append(seq)
  y_test.append(target)

x_train = np.array(x_train)
y_train = np.array(y_train)
x_test = np.array(x_test)
y_test = np.array(y_test)

# ----------------------------------------------------------------------------------------------------------------------
n_sequences, n_rows, n_cols = x_train.shape
scaler = StandardScaler()

x_train = x_train.reshape(-1, n_cols)
x_train = scaler.fit_transform(x_train)
x_train = x_train.reshape(-1, n_rows, n_cols)

x_test = x_test.reshape(-1, n_cols)
x_test = scaler.transform(x_test)
x_test = x_test.reshape(-1, n_rows, n_cols)

dump(scaler, open(file_path + 'rnn/rnn_scaler.pkl', 'wb'))

# ----------------------------------------------------------------------------------------------------------------------
# Hyperparameters
n_epochs = 100
batch_size = 32

# ----------------------------------------------------------------------------------------------------------------------
# RNN
eur_usd_rnn = Sequential()

eur_usd_rnn.add(GRU(128, return_sequences=True))
eur_usd_rnn.add(Dropout(0.2))
eur_usd_rnn.add(BatchNormalization())

eur_usd_rnn.add(GRU(128, return_sequences=True))
eur_usd_rnn.add(Dropout(0.1))
eur_usd_rnn.add(BatchNormalization())

eur_usd_rnn.add(GRU(128))
eur_usd_rnn.add(Dropout(0.2))
eur_usd_rnn.add(BatchNormalization())

eur_usd_rnn.add(Dense(32, activation='relu'))
eur_usd_rnn.add(Dropout(0.2))

eur_usd_rnn.add(Dense(3, activation='softmax'))

# ----------------------------------------------------------------------------------------------------------------------
early_stop = EarlyStopping(monitor='val_accuracy', verbose=1, patience=100)
model_checkpoint = ModelCheckpoint(file_path + 'rnn/rnn.h5', monitor='val_accuracy', save_best_only=True, verbose=1)
optimizer = Adam()

eur_usd_rnn.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

# ----------------------------------------------------------------------------------------------------------------------
history = eur_usd_rnn.fit(
    x_train, y_train,
    batch_size=batch_size,
    epochs=n_epochs,
    validation_data=(x_test, y_test),
    callbacks=[early_stop, model_checkpoint]
)

# ----------------------------------------------------------------------------------------------------------------------
eur_usd_rnn = load_model(file_path + 'rnn/rnn.h5')

# ----------------------------------------------------------------------------------------------------------------------
test_df = test_df.iloc[:, 0:-1]

# ----------------------------------------------------------------------------------------------------------------------
scaler = load(open(file_path + 'rnn/rnn_scaler.pkl', 'rb'))
test_df = scaler.transform(test_df)

# ----------------------------------------------------------------------------------------------------------------------
test_df.shape

# ----------------------------------------------------------------------------------------------------------------------
test_df[0, :]

# ----------------------------------------------------------------------------------------------------------------------
bid_open, bid_high, bid_low, bid_close, ask_open, ask_high, ask_low, ask_close = test_df[0, 0:8]

# ----------------------------------------------------------------------------------------------------------------------
test_df_sequences = deque(maxlen=60)

for i in range(0, 60):
    test_df_sequences.append(test_df[i, :])

reward = 0
n_wins = 0
n_losses = 0
win_streak = 0
loss_streak = 0
curr_win_streak = 0
curr_loss_streak = 0
n_buys = 0
n_sells = 0
trade_len = 0
trade_len_divider = 2 * 24
trade_lens = []
trade = None
open_price = None
stop_gain = None
stop_loss = None

for i in range(60, test_df.shape[0]):
    if account_balance + reward < 0:
        print(account_balance + reward)

    curr_seq = np.array(test_df_sequences)
    bid_open, bid_high, bid_low, bid_close, ask_open, ask_high, ask_low, ask_close = test_df[i, 0:8]

    if trade is None:
        pred = eur_usd_rnn.predict(curr_seq.reshape(1, 60, 84))

        if np.argmax(pred) == 1:
            trade = 'buy'
            open_price = float(round(ask_open, 5))
            stop_gain = round(open_price + (1.5 * pips_to_risk), 5)
            stop_loss = round(open_price - pips_to_risk, 5)
            n_buys += 1

        elif np.argmax(pred) == 2:
            trade = 'sell'
            open_price = float(round(bid_open, 5))
            stop_gain = round(open_price - (1.5 * pips_to_risk), 5)
            stop_loss = round(open_price + pips_to_risk, 5)
            n_sells += 1

    test_df_sequences.append(test_df[i, :])

    if trade is not None:
        trade_len += 1
        if trade == 'buy':
            if bid_low <= stop_loss:
                loss_amount = (stop_loss - open_price) * 10000 * value_per_pip
                if loss_amount > 0:
                    print('here1')
                    print(loss_amount)
                    break
                reward += loss_amount
                n_days = math.floor(trade_len / trade_len_divider)
                reward -= 0.8 * n_days
                n_losses += 1 if stop_loss != open_price else 0
                curr_loss_streak += 1 if stop_loss != open_price else 0
                curr_win_streak = 0
                loss_streak = max(loss_streak, curr_loss_streak)

                trade = None
                trade_lens.append(trade_len)
                trade_len = 0

                continue

            if bid_high >= open_price + pips_to_risk:
                stop_loss = open_price

            if bid_high >= stop_gain:
                win_amount = (stop_gain - open_price) * 10000 * value_per_pip
                if win_amount < 0:
                    print('here2')
                    print(win_amount)
                    break
                reward += win_amount
                n_days = math.floor(trade_len / trade_len_divider)
                reward -= 0.8 * n_days
                n_wins += 1
                curr_loss_streak = 0
                curr_win_streak += 1
                win_streak = max(win_streak, curr_win_streak)

                trade = None
                trade_lens.append(trade_len)
                trade_len = 0

                continue

        elif trade == 'sell':
            if ask_high >= stop_loss:
                loss_amount = (open_price - stop_loss) * 10000 * value_per_pip
                if loss_amount > 0:
                    print('here3')
                    print(loss_amount)
                    break
                reward += loss_amount
                n_days = math.floor(trade_len / trade_len_divider)
                reward -= 0.8 * n_days
                n_losses += 1 if stop_loss != open_price else 0
                curr_loss_streak += 1 if stop_loss != open_price else 0
                curr_win_streak = 0
                loss_streak = max(loss_streak, curr_loss_streak)

                trade = None
                trade_lens.append(trade_len)
                trade_len = 0

                continue

            if ask_low <= open_price - pips_to_risk:
                stop_loss = open_price

            if ask_low <= stop_gain:
                win_amount = (open_price - stop_gain) * 10000 * value_per_pip
                if win_amount < 0:
                    print('here4')
                    print(win_amount)
                    break
                reward += win_amount
                n_days = math.floor(trade_len / trade_len_divider)
                reward -= 0.8 * n_days
                n_wins += 1
                curr_loss_streak = 0
                curr_win_streak += 1
                win_streak = max(win_streak, curr_win_streak)

                trade = None
                trade_lens.append(trade_len)
                trade_len = 0

                continue

# ----------------------------------------------------------------------------------------------------------------------
print('Number of wins: ' + str(n_wins))
print('Number of losses: ' + str(n_losses))
print('Longest win streak: ' + str(win_streak))
print('Longest loss streak: ' + str(loss_streak))
print('Buys: ' + str(n_buys))
print('Sells: ' + str(n_sells))
print('Total trades: ' + str(n_buys + n_sells))
print('Average trade length: ' + str(sum(trade_lens) / len(trade_lens)))
print('Reward: $' + str(reward))
# ----------------------------------------------------------------------------------------------------------------------

