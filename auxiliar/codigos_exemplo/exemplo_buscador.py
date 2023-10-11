from selenium import webdriver  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC  
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException  
from selenium.webdriver.common.keys import Keys  
import smtplib 
  
x = "2020-03-10" 
y = "2020-03-16"
  
a = int(x[8:10]) 
b = int(y[8:10]) 
  
if a > b: 
    m = a - b 
    t = b 
  
else: 
    m = b - a 
    t = a 
print(t) 
  
low_price = "" 
url_final = 'https://paytm.com/flights'
data = {} 
  
for i in range(t, t + m+1): 
    url = 'https://paytm.com/flights/flightSearch/BBI-\Bhubaneshwar/DEL-Delhi/1/0/0/E/2023-11-'+str(i) 
      

    
    print(url) 
      
    date = "2019-12-" + str(i) 
      
    
    
    chrome_options = Options() 
    chrome_options.add_argument("--disable-gpu") 
      
  
    chrome_options.add_argument("--headless") 
      
    driver = webdriver.Chrome(executable_path = '/path/to/chromedriver',  
                              options=chrome_options) 
      
    driver.implicitly_wait(20) # indica ao navegador que deve aguardar um determinado tempo quando tentar buscar um elemento do DOM e não encontrar
    driver.get(url) 
      
    g = driver.find_element_by_xpath("//div[@class='_2gMo']")  
    price = g.text 
      
    x = price[0] 
    y = price[2:5] 
    z = str(x)+str(y) 
    p = int(z) 
    print(p) 
      
    prices=[] 
    if p <= 2000: 
        data[date] = p 
          
for i in data: 
    low_price += str(i) + ": Rs." + str(data[i]) + "\n"
      
print(low_price)  
  
if len(data) != 0: 
      
    dp = 2000
    server = smtplib.SMTP('smtp.gmail.com',587) 
    server.ehlo() 
    server.starttls() 
    server.ehlo() 
      
    server.login('your_email_id','your_password') 
    subject = "Flight price for BBI-DEL has fallen\below Rs. " + str(dp) 
      
    body = "Hey Akash! \n The price of BBI-DEL on PayTm \has fallen down below Rs." + str(dp) + ".\n So,\hurry up & check: " + url_final+"\n\n\n The prices of\flight below Rs.2000 for the following days are\:\n\n" + low_price 
      
    msg = f"Subject: {subject} \n\n {body}"
      
    server.sendmail( 
      
        'email_id_1', 
        'email_id_2', 
        msg 
        ) 
      
    print("HEY,EMAIL HAS BEEN SENT SUCCESSFULLY.") 
       
    server.quit() 