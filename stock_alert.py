import requests
import json
import datetime
import time
from yahoo_fin import stock_info as si


class StockAlert:
  """Receive notifications whenever a stock reaches a percentage of variation since the Open price.
  
  Ex:
    > stock_alert = StockAlert('ENB.TO', -.01, ACCESS_TOKEN='...')
    > stock_alert(loops = 60 * 6)
  """

  def __init__(self, ticker, percentage_threshold, ACCESS_TOKEN, *,
               sleep_seconds = 60,
               notify_only_once = True,
               api_url = 'https://api.pushbullet.com/v2/pushes',
               ):
    self.ticker = ticker #(str): stock ticker id (ie: AAPL)
    self.sleep_seconds = sleep_seconds #(int): time between loops of stock check
    self.percentage_threshold = percentage_threshold #(float): alert above/beyond the stock open price
    self.ACCESS_TOKEN = ACCESS_TOKEN #(str): pushbullet API access token
    self.api_url = api_url #(str): URL for the pushbullet API
    self.notify_only_once = notify_only_once #(bool): break loop when a notification is sent


  def _notify(self, title, body):
    """ Send notification via pushbullet.
        Args:
            title (str) : title of text.
            body (str) : Body of text.
    """
    # https://simply-python.com/2015/03/23/sending-alerts-to-iphone-or-android-phone-using-python/

    data_send = {"type": "note", "title": title, "body": body}
 
    resp = requests.post(self.api_url, data=json.dumps(data_send),
                    headers={'Authorization': 'Bearer ' + self.ACCESS_TOKEN,
                             'Content-Type': 'application/json'})
    if resp.status_code != 200:
        raise Exception('Notification not sent. Something wrong!')
    # else:
    #     print('complete sending')
    

  def __call__(self, loops=2):
    """ Monitors the live stock price and send notification if reached the threshold.
        Args:
            loops (int) : Maximum loops of stopck check.
    """

    for loop in range(loops):

      # get live stock price
      table = si.get_quote_table(self.ticker)
      
      # calculate the variation of live price in relation to open
      open = table['Open']
      price = table['Quote Price']
      percentage_variation = (price - open) / open

      # print('{:.2f} {:.1%}'.format(price, percentage_variation)) # for debug purpose

      # send alert if condition is satisfied
      send_alert = (self.percentage_threshold > 0) and (percentage_variation > self.percentage_threshold) \
                or (self.percentage_threshold < 0) and (percentage_variation < self.percentage_threshold)
      if send_alert:        
        self._notify(self.ticker, 'reached {:.2f}'.format(price))
        print('alert sent for {} at price {:.2f} variation:{:.1%} threshold:{:.1%} {}'.format(
            self.ticker, price, percentage_variation, self.percentage_threshold, str(datetime.datetime.now().strftime('at %H:%M:%S of %D'))))
        
        if self.notify_only_once:
          # exit loop
          break
        
      if loop < loops - 1:
        # wait a while before resuming the next loop
        time.sleep(self.sleep_seconds)