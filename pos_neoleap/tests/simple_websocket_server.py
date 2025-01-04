import asyncio
import logging
import websockets
import random
import json
import time


async def handler(websocket):
    while True:
        message = await websocket.recv()
        print(message)
        event = json.loads(message)
        action_type = event.get('Command', False)
        response = {}
        if action_type == "CHECK_STATUS":
            print('action_type', action_type)
            terminal_status = True   # random.choice([True, False])
            print('terminal_status', terminal_status)
            if terminal_status:
                response = {
                    "EventName": "TERMINAL_STATUS",
                    "TerminalStatus": "READY"
                }
            else:
                response = {
                    "EventName": "TERMINAL_STATUS",
                    "TerminalStatus": "BUSY"
                }
        if action_type == 'SALE':
            # accepted_trx = random.choice([True, False])
            accepted_trx = True
            amount_trx = event.get('Amount', 0)
            auth_code = random.randint(99999, 1000000)
            ecr_ref = random.randint(9999, 100000)
            print("Amount_trx", amount_trx)
            if accepted_trx:
                response = {
                    "API_Status": "0",      # important
                    "EventName": "TERMINAL_RESPONSE",
                    "JsonResult": {
                        "StatusCode": "00",
                        "MerchantNameEnglish": "mada Test",
                        "MerchantNameArabic": " إختبارمدى ",
                        "MerchantAddress1English": "Al-Olaya, Riyadh",
                        "MerchantAddress2English": "",
                        "MerchantAddress1Arabic": " العليا,الرياض ",
                        "MerchantAddress2Arabic": "رياض",
                        "download_phone": "123456789018",
                        "TransactionDateTime": "20211230105922",
                        "TransacitonRequestDateTime": "20211230105922",
                        "TransactionResponseDateTime": "20211230105922",
                        "BankId": "RYDB",
                        "CardAcceptorIdCode": "650999000911 ",
                        "CardAcceptorTerminalId": "1234567812121250",
                        "TerminalVersion": "1.2.13",
                        "CardAcceptorBusinessCode": "5411",
                        "TransactionSTAN": "000085",
                        "RetrievalReferenceNumber": "136410000085",
                        "CardSchemeID": "P1",
                        "CardNameArabic": "مدى",
                        "CardNameEnglish": "mada",
                        "CardScheme": "mada",
                        "PrimaryAccountNumber": "484783******6960",
                        "CardExpiryDate": "2310",
                        "TransactionTypeArabic": "شراء",
                        "TransactionTypeEnglish": "PURCHASE",
                        "TransactionAmount": "100.00",
                        "TransactionResponseEnglish": "APPROVED",                 # important
                        "TransactionResponseArabic": "مقبولة",
                        "TransactionResultReasonEnglish": "APPROVED",
                        "TransactionResultReasonArabic": "مقبولة",
                        "ResponseCodeDescription": " اليتطلبالتحقق |NO VERIFICATION REQUIRED",
                        # important
                        "TransactionAuthCode": str(auth_code),
                        "TerminalModel": "NewlandN910",
                        "POSEntryMode": "CONTACTLESS",
                        "TransactionResponse": "000",
                        "AID": "A0000002282010",
                        "TVR": "0000000000",
                        "TSI": "0000",
                        "CryptResult": "80",
                        "ApplicationCryptogram": "5110ABB2B29C0494",
                        "KID": "03",
                        # important
                        "ECRReferenceNumber": str(ecr_ref)
                    }
                }
            else:
                response = {
                    "API_Status": "0",
                    "EventName": "TERMINAL_RESPONSE",
                    "JsonResult": {
                        "StatusCode": "01",
                        "MerchantNameEnglish": "mada Test",
                        "MerchantNameArabic": " إختبارمدى ",
                        "MerchantAddress1English": "Al-Olaya, Riyadh",
                        "MerchantAddress2English": "",
                        "MerchantAddress1Arabic": " العليا,الرياض ",
                        "MerchantAddress2Arabic": "رياض",
                        "download_phone": "123456789018",
                        "TransactionDateTime": "20211206070926",
                        "TransacitonRequestDateTime": "20211206070926",
                        "TransactionResponseDateTime": "20211206070926",
                        "BankId": "RYDB",
                        "CardAcceptorIdCode": "650999000911 ",
                        "CardAcceptorTerminalId": "1234567812121250",
                        "TerminalVersion": "1.2.13",
                        "CardAcceptorBusinessCode": "5411",
                        "TransactionSTAN": "000052",
                        "RetrievalReferenceNumber": "134007000052",
                        "CardSchemeID": "P1",
                        "CardNameEnglish": "mada",
                        "CardSchemeArabic": "مدى",
                        "CardSchemeEnglish": "mada",
                        "CardScheme": "mada",
                        "PrimaryAccountNumber": "585265******753200",
                        "CardExpiryDate": "2212",
                        "TransactionTypeArabic": "شراء",
                        "TransactionTypeEnglish": "PURCHASE",
                        "TransactionAmount": str(amount_trx),
                        "TransactionResponseEnglish": "DECLINED",
                        "TransactionResultReasonEnglish": "DECLINED",
                        "TransactionResponseArabic": "مرفوضة",
                        "TransactionResultReasonArabic": "مرفوضة",
                        "TerminalModel": "NewlandN910",
                        "POSEntryMode": "CONTACTLESS",
                        "TransactionResponse": "100",
                        "AID": "A0000002281010",
                        "TVR": "0400000001",
                        "TSI": "0000",
                        "CVMResult": "1F0302",
                        "CryptResult": "80",
                        "ApplicationCryptogram": "3BA668DECD1650A5",
                        "KID": "02",
                        "ECRReferenceNumber": str(ecr_ref)
                    }
                }
            time.sleep(300)
            response_xml = False
            if response_xml:
                response = '{\"API_Status\":\"0\" , \"EventName\":\"TERMINAL_RESPONSE\", ?xml version=\"1.0\" encoding=\"windows-1256\" standalone=\"no\" ?><madaTransactionResult><Retailer RetailerNameEng=\"Gissah Perfume Co\" RetailerNameArb=\"شركة قصة للعطور\" address_eng_1=\"Panorama MallRiyadh\" address_eng_2=\"\" address_arb_1=\"بانوراما مول\" address_arb_2=\"الرياض\" download_phone=\"\"/><Performance StartDateTime=\"24102023175731\" EndDateTime=\"24102023175732\"/><BankId>RAJB</BankId><MerchantID>805362001906</MerchantID><TerminalID>8136012001194761</TerminalID><MCC>5947</MCC><STAN>000047</STAN><Version>1.2.54</Version><RRN>329705000047</RRN><CardScheme ID=\"P1\" Arabic=\"مدى\" English=\"mada\"/><ApplicationLabel Arabic=\"مدى\" English=\"mada\"/><PAN>506968****8338</PAN><CardExpiryDate>2410</CardExpiryDate><TransactionType Arabic=\"شراء\" English=\"PURCHASE\"/><Amounts ArabicCurrency=\"ريال\"  EnglishCurrency=\"SAR\"><Amount ArabicName=\"مبلغ الشراء\" EnglishName=\"PURCHASE AMOUNT\" >0.01</Amount></Amounts><Result Arabic=\"مقبولة\" English=\"APPROVED\"/><CardholderVerification Arabic=\"تم التحقق من هوية حامل الجهاز\" English=\"DEVICE OWNER IDENTITY VERIFIED\"/><ApprovalCode Arabic = \"رمز الموافقة\" English=\"APPROVAL CODE\">175800</ApprovalCode><EMV_Tags><PosEntryMode>CONTACTLESS</PosEntryMode><ResponseCode>000</ResponseCode><TerminalStatusCode>00</TerminalStatusCode><AID>A0000002281010</AID><TVR>0080008800</TVR><TSI>0000</TSI><CVR>3F0000</CVR><ACI>80</ACI><AC>7249E65C365C7DA7</AC><KID>2D</KID><PAR>012923R0305NJFB9UUM6T757UK5XN2XHJ</PAR><FPAN>8428</FPAN></EMV_Tags><Campaign><QrCodeData></QrCodeData><CampaignText></CampaignText></Campaign><AdditionalData>33088-002-0002</AdditionalData></madaTransactionResult>'
        print('response', response)
        time.sleep(2)
        await websocket.send(json.dumps(response))
        continue


async def main():
    async with websockets.serve(handler, "", 7000):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
