import pandas as pd
import pathlib
import itertools
import math


def get_diff_count_units (diff): 
	_count_1 = _count_0 = _units_traded_1 = _units_traded_0 = 0 
	_price_1 = _price_0 = 0 

	diff_len = len (diff) 
	if diff_len == 1: 
		row = diff.iloc[0] 
		if row['type'] == 1: 
			_count_1 = row['count'] 
			_units_traded_1 = row['units_traded'] 
			_price_1 = row['price'] 
		else: 
			_count_0 = row['count'] 
			_units_traded_0 = row['units_traded'] 
			_price_0 = row['price'] 

		return (_count_1, _count_0, _units_traded_1, _units_traded_0, _price_1, _price_0) 

	elif diff_len == 2: 
		row_1 = diff.iloc[1] 
		row_0 = diff.iloc[0] 
		_count_1 = row_1['count'] 
		_count_0 = row_0['count'] 

		_units_traded_1 = row_1['units_traded'] 
		_units_traded_0 = row_0['units_traded'] 

		_price_1 = row_1['price'] 
		_price_0 = row_0['price'] 

		return (_count_1, _count_0, _units_traded_1, _units_traded_0, _price_1, _price_0) 





def live_cal_book_d_v1(param, gr_bid_level, gr_ask_level, diff, var, mid): 

	ratio = param[0]; level = param[1]; interval = param[2] 
	
	decay = math.exp(-1.0/interval) 

	_flag = var['_flag'] 
	prevBidQty = var['prevBidQty'] 
	prevAskQty = var['prevAskQty'] 
	prevBidTop = var['prevBidTop'] 
	prevAskTop = var['prevAskTop'] 
	bidSideAdd = var['bidSideAdd'] 
	bidSideDelete = var['bidSideDelete'] 
	askSideAdd = var['askSideAdd'] 
	askSideDelete = var['askSideDelete'] 
	bidSideTrade = var['bidSideTrade'] 
	askSideTrade = var['askSideTrade'] 
	bidSideFlip = var['bidSideFlip'] 
	askSideFlip = var['askSideFlip'] 
	bidSideCount = var['bidSideCount'] 
	askSideCount = var['askSideCount'] 

	curBidQty = gr_bid_level['quantity'].sum() 
	curAskQty = gr_ask_level['quantity'].sum() 
	curBidTop = gr_bid_level.iloc[0].price
	curAskTop = gr_ask_level.iloc[0].price 


	if _flag: 
		var['prevBidQty'] = curBidQty 
		var['prevAskQty'] = curAskQty 
		var['prevBidTop'] = curBidTop 
		var['prevAskTop'] = curAskTop 
		var['_flag'] = False 
		return 0.0 

	if curBidQty > prevBidQty: 
		bidSideAdd += 1 
		bidSideCount += 1 
	if curBidQty < prevBidQty: 
		bidSideDelete += 1 
		bidSideCount += 1 
	if curAskQty > prevAskQty: 
		askSideAdd += 1 
		askSideCount += 1 
	if curAskQty < prevAskQty: 
		askSideDelete += 1 
		askSideCount += 1 

	if curBidTop < prevBidTop: 
		bidSideFlip += 1 
		bidSideCount += 1 
	if curAskTop > prevAskTop: 
		askSideFlip += 1 
		askSideCount += 1 


	(_count_1, _count_0, _units_traded_1, _units_traded_0, _price_1, _price_0) = diff 
	
	bidSideTrade += _count_1 
	bidSideCount += _count_1 

	askSideTrade += _count_0 
	askSideCount += _count_0 


	if bidSideCount == 0: 
		bidSideCount = 1 
	if askSideCount == 0: 
		askSideCount = 1 

	bidBookV = (-bidSideDelete + bidSideAdd - bidSideFlip) / (bidSideCount**ratio) 
	askBookV = (askSideDelete - askSideAdd + askSideFlip ) / (askSideCount**ratio) 
	tradeV = (askSideTrade/askSideCount**ratio) - (bidSideTrade / bidSideCount**ratio) 
	bookDIndicator = askBookV + bidBookV + tradeV 


	var['bidSideCount'] = bidSideCount * decay
	var['askSideCount'] = askSideCount * decay 
	var['bidSideAdd'] = bidSideAdd * decay 
	var['bidSideDelete'] = bidSideDelete * decay 
	var['askSideAdd'] = askSideAdd * decay 
	var['askSideDelete'] = askSideDelete * decay 
	var['bidSideTrade'] = bidSideTrade * decay 
	var['askSideTrade'] = askSideTrade * decay 
	var['bidSideFlip'] = bidSideFlip * decay 
	var['askSideFlip'] = askSideFlip * decay 

	var['prevBidQty'] = curBidQty 
	var['prevAskQty'] = curAskQty 
	var['prevBidTop'] = curBidTop 
	var['prevAskTop'] = curAskTop 

	return bookDIndicator 



def live_cal_book_i_v1(param, gr_bid_level, gr_ask_level, diff, var, mid): 

	mid_price = mid 

	ratio = param[0]; level = param[1]; interval = param[2] 
	

	quant_v_bid = gr_bid_level.quantity**ratio 
	price_v_bid = gr_bid_level.price * quant_v_bid 

	quant_v_ask = gr_ask_level.quantity**ratio 
	price_v_ask = gr_ask_level.price * quant_v_ask 

	
	askQty = quant_v_ask.values.sum() 
	bidPx = price_v_bid.values.sum() 
	bidQty = quant_v_bid.values.sum() 
	askPx = price_v_ask.values.sum() 
	bid_ask_spread = interval 

	book_price = 0
	if bidQty > 0 and askQty > 0: 
		book_price = (((askQty*bidPx)/bidQty) + ((bidQty*askPx)/askQty)) / (bidQty+askQty) 


	indicator_value = (book_price - mid_price) / bid_ask_spread 
	
	return indicator_value 





def cal_mid_price (gr_bid_level, gr_ask_level, group_t): 

	level = 5 
	
	if len(gr_bid_level) > 0 and len(gr_ask_level) > 0: 
		bid_top_price = gr_bid_level.iloc[0]['price'] 
		bid_top_level_qty = gr_bid_level.iloc[0]['quantity'] 
		ask_top_price = gr_ask_level.iloc[0]['price'] 
		ask_top_level_qty = gr_ask_level.iloc[0]['quantity'] 
		mid_price = (bid_top_price + ask_top_price) * 0.5 


		return (mid_price, bid_top_price, ask_top_price, bid_top_level_qty, ask_top_level_qty) 

	else: 
		print('Error: serious cal_mid_price') 
		return (-1, -1, -2, -1, -1) 







filePath = str(pathlib.Path(__file__).parent.resolve()) 

book_df = pd.read_csv(filePath + '/2023-05-10-upbit-BTC-book.csv').apply(pd.to_numeric,errors='ignore') 
trade_df = pd.read_csv(filePath + '/2023-05-10-upbit-BTC-trade.csv').apply(pd.to_numeric,errors='ignore') 

gr_bdf_ts = book_df.groupby('timestamp') 
gr_tdf_ts = trade_df.groupby('timestamp') 

var = { 
	'_flag': True, 
	'prevBidQty': 0, 
	'prevAskQty': 0, 
	'prevBidTop': 0, 
	'prevAskTop': 0, 
	'bidSideAdd': 0, 
	'bidSideDelete': 0, 
	'askSideAdd': 0, 
	'askSideDelete': 0, 
	'bidSideTrade': 0, 
	'askSideTrade': 0, 
	'bidSideFlip': 0, 
	'askSideFlip': 0, 
	'bidSideCount': 0, 
	'askSideCount': 0 
} 

output_df = {'book-delta-v1-0.2-5-1': [], 'book-imbalance-0.2-5-1': [], 'mid_price': [], 'timestamp': []} 

trade_df_idx = trade_df.set_index('timestamp') 
for timestamp, group_bdf in gr_bdf_ts: 
	gr_bid_level = group_bdf[group_bdf['type'] == 0] 
	gr_ask_level = group_bdf[group_bdf['type'] == 1] 

	if timestamp not in trade_df_idx.index: 
		continue 
	group_tdf = trade_df_idx.loc[[timestamp]] 
	diff = get_diff_count_units(group_tdf) 

	(mid_price, bid_top_price, ask_top_price, bid_top_level_qty, ask_top_level_qty) = cal_mid_price(gr_bid_level, gr_ask_level, 0) 

	book_imbalance = live_cal_book_i_v1([0.2, 5, 1], gr_bid_level, gr_ask_level, diff, var, mid_price) 

	book_delta = live_cal_book_d_v1([0.2, 5, 1], gr_bid_level, gr_ask_level, diff, var, mid_price) 
	
	if book_delta == 0: 
		continue 

	output_df['book-delta-v1-0.2-5-1'].append(book_delta) 
	output_df['book-imbalance-0.2-5-1'].append(book_imbalance) 
	output_df['mid_price'].append(mid_price) 
	output_df['timestamp'].append(timestamp) 

pd.DataFrame(output_df).to_csv(filePath + '/2023-05-10-upbit-BTC-feature.csv', index = True) 
