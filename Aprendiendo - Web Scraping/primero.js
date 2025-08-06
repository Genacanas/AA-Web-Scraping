function run() {
    var inputs = [
      { 
        "url":"https://scstrade.com/Default.aspx",
        "filters" : [
          {
           "pattern": "<span.*id=\"ContentPlaceHolder1_lbl_kse100_index\".*style=\"color:Green;font-size:medium;font-weight:bold;\">(.*)/span>",
           "transformers": [toNumber,round]  
          }
        ],
        "label":"PSX>",
        "section":"Stocks"
      },
      { 
        "url":"https://scstrade.com/Default.aspx",
        "filters" : [
          {
           "pattern": "<span.*id=\"ContentPlaceHolder1_lbl_kse100_index\".*style=\"color:Red;font-size:medium;font-weight:bold;\">(.*)/span>",
           "transformers": [toNumber,round]  
          }
        ],
        "label":"PSX<",
        "section":"Stocks"
      },
      { 
        "url":"https://english.mubasher.info/markets/DFM",
        "filters" : [
          {
           "pattern": "<div.*\market-summary__last-price up-icon-only\">(.*)<\/div>",
           "transformers": [toNumber,round]  
          }
        ],
        "label":"DFM>",
        "section":"Stocks"
      },
      { 
        "url":"https://english.mubasher.info/markets/DFM",
        "filters" : [
          {
           "pattern": "<div.*\market-summary__last-price unchanged-icon-only\">(.*)<\/div>",
           "transformers": [toNumber,round]  
          }
        ],
        "label":"DFM<>",
        "section":"Stocks"
      },
      { 
        "url":"https://english.mubasher.info/markets/DFM",
        "filters" : [
          {
           "pattern": "<div.*\market-summary__last-price down-icon-only\">(.*)<\/div>",
           "transformers": [toNumber,round]  
          }
        ],
        "label":"DFM<",
        "section":"Stocks"
      },
      { 
        "url":"https://english.mubasher.info/markets/ADX",
        "filters" : [
          {
           "pattern": "<div.*\market-summary__last-price up-icon-only\">(.*)<\/div>",
           "transformers": [toNumber,round]  
          }
        ],
        "label":"ADX>",
        "section":"Stocks"
      },
      { 
        "url":"https://english.mubasher.info/markets/ADX",
        "filters" : [
          {
           "pattern": "<div.*\market-summary__last-price unchanged-icon-only\">(.*)<\/div>",
           "transformers": [toNumber,round]  
          }
        ],
        "label":"ADX<>",
        "section":"Stocks"
      },
      { 
        "url":"https://english.mubasher.info/markets/ADX",
        "filters" : [
          {
           "pattern": "<div.*\market-summary__last-price down-icon-only\">(.*)<\/div>",
           "transformers": [toNumber,round]  
          }
        ],
        "label":"ADX<",
        "section":"Stocks"
      },
      { 
        "url":"https://www.google.com/finance/quote/NCI:INDEXNASDAQ",
        "filters" : [
          {
           "pattern": "<div.*\YMlKec fxKbKc\">(.*)<\/div>",
           "transformers": [toNumber,round]  
          }
        ],
        "label":"NCI",
        "section":"Crypto"
      },
      { 
        "url":"https://api.alternative.me/fng/",
        "filters" : [
          {
           "pattern": "\"value\".*\"(.*)\"",
           "transformers": [extractNumber,toNumber]  
          }
        ],
        "label":"FGI",
        "section":"Crypto"
      },
      { 
        "url":"https://www.coindesk.com/price/cd20/",
        "filters" : [
          {
           "pattern": "<span.*\Noto_Sans_2xl_Sans-700-2xl text-color-black \">(.*)<\/span>",
           "transformers": [extractNumber,toNumber,round]  
          }
        ],
        "label":"CD20",
        "section":"Crypto"
      },
      { 
        "url":"https://markets.businessinsider.com/commodities/oil-price",
        "filters" : [
          {
           "pattern": "<span.*\price-section__current-value\">(.*)<\/span>",
           "transformers": [toNumber,round,formatUSD]  
          },
        ],
        "label":"Brent",
        "section":"Commodity"
      },
      { 
        "url":"https://igold.ae/", 
        "filters" : [
          {
           "pattern":"<div.*\col chart-content pr-1\">(.*)<\/div>",
           "transformers": [toNumber,round,formatAED]  
          },
        ],
        "label":"Gold",
        "section":"Commodity"
      },
      { 
        "url":"https://www.urdupoint.com/business/inter-bank-currency-rates-in-pakistan.html",
        "filters" : [
          {
           "pattern":"<td.*class=\"ac\".*><a.*class=\"db\".*href=\"https://www.urdupoint.com/business/usd-to-pkr.html\".*><span.*class=\"txt_label txt_label_gray\".*>(.*)<\/span>",
           "transformers": [extractNumber,toNumber,convertusdtoaed,formatPKR]  
          }
        ],
        "label":"AED-PKR-InterBank",
        "section":"Currency"
      },
      { 
        "url":"https://www.urdupoint.com/business/foreign-exchange-rates-in-pakistan.html",
        "filters" : [
          {
           "pattern":"<td.*class=\"ac\".*><a.*class=\"db\".*href=\"https://www.urdupoint.com/business/aed-to-pkr.html\".*><span.*class=\"txt_label txt_label_green\".*>(.*)<\/span>",
           "transformers": [extractNumber,toNumber,round2,formatPKR]  
          }
        ],
        "label":"AER-PKR-Forex",
        "section":"Currency"
      },
      { 
        "url":"https://www.urdupoint.com/business/open-market-currency-rates-in-pakistan.html",
        "filters" : [
          {
           "pattern":"<td.*class=\"ac\".*><a.*class=\"db\".*href=\"https://www.urdupoint.com/business/aed-to-pkr.html\".*><span.*class=\"txt_label txt_label_gray\".*>(.*)<\/span>",
           "transformers": [extractNumber,toNumber,round2,formatPKR]  
          }
        ],
        "label":"AED-PKR-Open",
        "section":"Currency"
      },
      { 
        "url":"https://www.binance.com/en/price/tether/PKR",
        "filters" : [
          {
           "pattern":"<meta.*\Live price of Tether USDt is ₨(.*).*\with a market cap of.*\/>",
           "transformers": [extractNumber,toNumber,convertusdtoaed,formatPKR]
          }
        ],
        "label":"AED-PKR-Binance",
        "section":"Currency"
      }
    ]
    
    var parameters = {};
    var items = doScrape(inputs);
    for (var index in items) {
      var item = items[index];
      if (item.result != undefined) {      
        var text = item.result;
        Logger.log(text);
        var section = item.input.section;
        if (!parameters[section]) {
          parameters[section] = [];
        }
        parameters[section].push({label: item.input.label, value: text});
      }
    }
    
    const binanceData = getBinanceData();
    if (binanceData) {
        if (!parameters["Currency"]) {
            parameters["Currency"] = [];
        }
        parameters["Currency"].push({ label: "Lowest-PKR", value: binanceData.pkrPrice });
        parameters["Currency"].push({ label: "Lowest-AED", value: binanceData.aedPrice });
        parameters["Currency"].push({ label: "AED-PKR-Binance", value: binanceData.calculatedRate });
    }

    Logger.log(parameters);
    sendMail(parameters);
  }
  
  // Función para obtener datos de Binance
function getBinanceData() {
    const pkrPrice = getLowestPrice("PKR");
    const aedPrice = getLowestPrice("AED");

    if (pkrPrice && aedPrice) {
        const calculatedRate = (pkrPrice / aedPrice).toFixed(2);
        Logger.log(`Calculated AED-PKR Rate: ${calculatedRate}`);
        return {
            pkrPrice: `PK.${pkrPrice}`,
            aedPrice: `AE.${aedPrice}`,
            calculatedRate: `PKR ${calculatedRate}`
        };
    } else {
        Logger.log("Failed to retrieve one or both prices.");
        return null;
    }
}

// Obtener precios desde Binance
function getLowestPrice(fiatCurrency) {
    const url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search";
    const payload = {
        "asset": "USDT",
        "fiat": fiatCurrency,
        "tradeType": "BUY",
        "page": 1,
        "rows": 10
    };

    const options = {
        "method": "post",
        "contentType": "application/json",
        "payload": JSON.stringify(payload)
    };

    try {
        const response = UrlFetchApp.fetch(url, options);
        const data = JSON.parse(response.getContentText());

        if (data && data.data && data.data.length > 0) {
            const lowestPrice = data.data[0].adv.price;
            Logger.log(`Lowest price for ${fiatCurrency}: ${lowestPrice}`);
            return parseFloat(lowestPrice);
        } else {
            Logger.log(`No data found for ${fiatCurrency}`);
            return null;
        }
    } catch (e) {
        Logger.log(`Error fetching price for ${fiatCurrency}: ${e.message}`);
        return null;
    }
}

  function doScrape(inputs) {
    var results = [];
    for (var index in inputs) {
      var input = inputs[index];
      Logger.log("scraping data from " + input.url);
      var result = getData(input.url, input.filters);
      Logger.log("finished scraping data from" + input.url + " with result " + result);
      results.push({ "input": input,"result": result });
    };
    return results;
  }
  
  function getData(url,filters) {
    var values = [];
    try {
    var html = UrlFetchApp.fetch(url).getContentText();
    //Logger.log(html);
    for(var index in filters) {
      var filter = filters[index];
      var regexp = new RegExp(filter.pattern);
      var result = regexp.exec(html);
      if (result != undefined) {
        Logger.log(result);
        var value = normalize(result[1].toString());
        if (value !== "") {
          if (filter.transformers) {
            for(var index in filter.transformers) {
              var transformer = filter.transformers[index];
              value = transformer(value);
            }
          }
          values.push(value);
        }
      }
    }} catch(e) {
      Logger.log(e);
    }
    
    if(values)
      return values.join(" ");
    return "";
  }
  
  function normalize(input) {
    input = input.trim();
    input = input.replace(/<[^>]+>/g, "");
    input = input.replace(/&nbsp;/g, ' ');
    input = input.replace(/\s+/g, ' ');
    return input;
  }
  
  function sendMail(parameters) {
    var email = "genaro0324@gmail.com"; // set target email, if not specified active user's email will be used
    var emailbcc = "";
    if (email === "") {
      email = Session.getActiveUser().getEmail();
    }
  
    var body = "";
    for(var key in parameters)
    {
      body = body + "<b>" + key + "</b>";
      var section = parameters[key];
      for(var index in section) {
        var item = section[index];
        if (item.label === "Gold" && item.value && item.value.length > 0) {
          var tokens = item.value.split(" ");
          if (tokens.length > 0) {
            body = body + "<pre>&#9;24K" + "&#9;" + tokens[0].replace(" ", "&#9;")+ "</pre>";
          }
          if (tokens.length > 1) {
            body = body + "<pre>&#9;22K" + "&#9;" + tokens[1].replace(" ", "&#9;") + "</pre>";
          }  
        } else {
          body = body + "<pre>&#9;" + item.label + "&#9;" + item.value.replace(" ", "&#9;") + "</pre>"; 
        }
      }
      body += "<br/>";
    }
  
    var html = "";
    html += "<!DOCTYPE html>";
    html += "<html lang=\"en\">";
    html += "<head>";
    html +=   "<meta charset=\"utf-8\">";
    html +=   "<title>Financial Info</title>";
      html += "<style type=\"text/css\">";
      html += "body {";
      html += "	font-family: Arial,Verdana,Helvetica,Tahoma,\"Times New Roman\",Georgia;";
      html += "}";
    html += "pre {";
    html += " font-family: Arial,Verdana,Helvetica,Tahoma,\"Times New Roman\",Georgia;";
    html += "}";
      html += "</style>";
    html += "</head>";
    html += "<body>";
    html += body;
    html += "</body>";
    html += "</html>";
  
    Logger.log("sending email with content:\n" + html);
    
    MailApp.sendEmail({
      to: email,
      bcc: emailbcc,
      subject: "Financial Info",
      htmlBody: html
    });
  
    Logger.log("email sent!")
  }
  
  function extractNumber(text) {
    return text.replace(/[^0-9\.]+/g,"");
  }
  
  function toNumber(text) {
    return parseFloat(text.replace(/,/g, ''))
  }
  
  function round(num) {
    return Math.round(num);
  }
  
  function round2(num) {
    return Math.round((num + Number.EPSILON) * 100) / 100;
  }
  
  function addpercentconvertaed(num) {
    return Math.round(((((num + (num * 0.02)) * 100) / 100)/ 3.6725) * 100) / 100;
  }
  
  function convertusdtoaed(num) {
    return Math.round((num / 3.6725) * 100) / 100;
  }
  function goldPrice(text) {
    var tokens = text.split(" ");
    if (tokens != null && tokens.length >= 3) {
      return tokens[2];
    }
    return text;
  }
  
  function formatUSD(value) {
    return "US." + value; 
  }
  
  function formatAED(value) {
    return "AE." + value; 
  }
  
  function formatPKR(value) {
    return "PK." + value; 
  }