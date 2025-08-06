function run() {
    // Datos originales del cliente y agregados
    var inputs = [
        { 
          "url":"https://scstrade.com/Default.aspx",
          "filters" : [
            {
             "pattern": "<span.*id=\"ContentPlaceHolder1_lbl_kse100_index\".*style=\"color:Green;font-size:medium;font-weight:bold;\">(.*?)</span>",
             "transformers": [toNumber, round]  
            }
          ],
          "label":"PSX>",
          "section":"Stocks"
        },
        { 
          "url":"https://scstrade.com/Default.aspx",
          "filters" : [
            {
             "pattern": "<span.*id=\"ContentPlaceHolder1_lbl_kse100_index\".*style=\"color:Red;font-size:medium;font-weight:bold;\">(.*?)</span>",
             "transformers": [toNumber, round]  
            }
          ],
          "label":"PSX<",
          "section":"Stocks"
        },
        { 
          "url":"https://english.mubasher.info/markets/DFM",
          "filters" : [
            {
             "pattern": "<div.*?market-summary__last-price (?:up|down|unchanged)-icon-only\">(.*?)</div>",
             "transformers": [toNumber, round]  
            }
          ],
          "label":"DFM",
          "section":"Stocks"
        },
        { 
          "url":"https://english.mubasher.info/markets/ADX",
          "filters" : [
            {
             "pattern": "<div.*?market-summary__last-price (?:up|down|unchanged)-icon-only\">(.*?)</div>",
             "transformers": [toNumber, round]  
            }
          ],
          "label":"ADX",
          "section":"Stocks"
        },
        { 
          "url":"https://www.google.com/finance/quote/NCI:INDEXNASDAQ",
          "filters" : [
            {
             "pattern": "<div.*?YMlKec fxKbKc\">(.*?)</div>",
             "transformers": [toNumber, round]  
            }
          ],
          "label":"NCI",
          "section":"Crypto"
        },
        { 
          "url":"https://api.alternative.me/fng/",
          "filters" : [
            {
             "pattern": "\"value\":\\s*\"(\\d+)\"",
             "transformers": [extractNumber, toNumber]  
            }
          ],
          "label":"FGI",
          "section":"Crypto"
        },
        { 
          "url":"https://www.coindesk.com/price/cd20/",
          "filters" : [
            {
             "pattern": "<span.*?Noto_Sans_2xl_Sans-700-2xl text-color-black \">(.*?)</span>",
             "transformers": [extractNumber, toNumber, round]  
            }
          ],
          "label":"CD20",
          "section":"Crypto"
        },
        { 
          "url":"https://markets.businessinsider.com/commodities/oil-price",
          "filters" : [
            {
             "pattern": "<span.*?price-section__current-value\">(.*?)</span>",
             "transformers": [toNumber, round, formatUSD]  
            }
          ],
          "label":"Brent",
          "section":"Commodity"
        },
        { 
          "url":"https://igold.ae/",
          "filters" : [
            {
             "pattern": "<div.*?col chart-content pr-1\">(.*?)</div>",
             "transformers": [toNumber, round, formatAED]  
            }
          ],
          "label":"Gold",
          "section":"Commodity"
        },
        // Agregar los datos de Currency faltantes
        { 
          "url":"https://www.urdupoint.com/business/inter-bank-currency-rates-in-pakistan.html",
          "filters" : [
            {
             "pattern":"<td.*class=\"ac\".*><a.*class=\"db\".*href=\"https://www.urdupoint.com/business/usd-to-pkr.html\".*><span.*class=\"txt_label txt_label_gray\".*>(.*?)</span>",
             "transformers": [extractNumber, toNumber, formatPKR]  
            }
          ],
          "label":"AED-PKR-InterBank",
          "section":"Currency"
        },
        { 
          "url":"https://www.urdupoint.com/business/foreign-exchange-rates-in-pakistan.html",
          "filters" : [
            {
             "pattern":"<td.*class=\"ac\".*><a.*class=\"db\".*href=\"https://www.urdupoint.com/business/aed-to-pkr.html\".*><span.*class=\"txt_label txt_label_green\".*>(.*?)</span>",
             "transformers": [extractNumber, toNumber, round2, formatPKR]  
            }
          ],
          "label":"AER-PKR-Forex",
          "section":"Currency"
        },
        { 
          "url":"https://www.urdupoint.com/business/open-market-currency-rates-in-pakistan.html",
          "filters" : [
            {
             "pattern":"<td.*class=\"ac\".*><a.*class=\"db\".*href=\"https://www.urdupoint.com/business/aed-to-pkr.html\".*><span.*class=\"txt_label txt_label_gray\".*>(.*?)</span>",
             "transformers": [extractNumber, toNumber, round2, formatPKR]  
            }
          ],
          "label":"AED-PKR-Open",
          "section":"Currency"
        }
    ];

    // Consolidar los resultados en parameters
    var parameters = {};
    var items = doScrape(inputs);

    // Procesar datos originales
    for (var index in items) {
        var item = items[index];
        if (item.result !== undefined) {
            var text = item.result;
            Logger.log(text);
            var section = item.input.section;
            if (!parameters[section]) {
                parameters[section] = [];
            }
            parameters[section].push({ label: item.input.label, value: text });
        }
    }

    // Añadir los datos de Binance
    const binanceData = getBinanceData();
    if (binanceData) {
        if (!parameters["Currency"]) {
            parameters["Currency"] = [];
        }
        parameters["Currency"].push({ label: "Lowest-PKR", value: binanceData.pkrPrice });
        parameters["Currency"].push({ label: "Lowest-AED", value: binanceData.aedPrice });
        parameters["Currency"].push({ label: "AED-PKR-Binance", value: binanceData.calculatedRate });
    }

    // Enviar el correo
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

// Función para enviar el correo
function sendMail(parameters) {
    const email = "genaro0324@gmail.com";
    var body = "";

    for (var key in parameters) {
        body += `<b>${key}</b><br/>`;
        var section = parameters[key];
        for (var index in section) {
            var item = section[index];
            body += `<pre>${item.label}&#9;${item.value}</pre>`;
        }
        body += "<br/>";
    }

    MailApp.sendEmail({
        to: email,
        subject: "Financial Info",
        htmlBody: body
    });

    Logger.log("Email sent successfully.");
}

