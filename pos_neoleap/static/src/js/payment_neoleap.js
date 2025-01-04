// import { PaymentWorldline } from "@pos_iot/app/payment";

// export class PaymentNeoleap extends PaymentWorldline{
//     /**
//     * @override
//     */
//     init() {
//         this._super.apply(this, arguments);
//         // this.enable_reversals();
//         console.log("I started to do something");
//         var terminal_ip = this.payment_method.neoleap_terminal_ip;
//         var instanced_payment_method = _.find(this.pos.payment_methods, function (payment_method) {
//             return payment_method.use_payment_terminal === "neoleap"
//                 && payment_method.neoleap_terminal_ip === terminal_ip
//                 && payment_method.payment_terminal;
//         });
//         if (instanced_payment_method !== undefined) {
//             var payment_terminal = instanced_payment_method.payment_terminal;
//             this.terminal = payment_terminal.terminal;
//             this.terminalListener = payment_terminal.terminalListener;
//             return;
//         }
//     }

//     send_payment_cancel() {
//         this._super.apply(this, arguments);
//         console.log('send_payment_cancel');
//         if (this._ws) {
//             console.log('send_payment_cancel2');
//             this._ws.close();
//         }
//         this.pos.get_order().selected_paymentline.set_payment_status('waiting');
//         try {
//             this.transactionReject(new Error('Cancelled Payment'));
//         } catch { }
//         return Promise.resolve();
//     }

//     send_payment_request(cid) {
//         let self = this;
//         this._super.apply(this, arguments);
//         console.log('send_payment_request');
//         let line = this.pos.get_order().selected_paymentline;
//         line.set_payment_status('waiting');
//         // return this._sendTransaction();
//         const timeout = (prom, time) => {
//             let timer;
//             return Promise.race([
//                 prom,
//                 new Promise((res, rej) => {
//                     timer = setTimeout(res, time)
//                 }).then((res) => {
//                     line.set_payment_status('force_done');
//                 })
//             ]).finally(() => clearTimeout(timer));
//         }
//         return timeout(this._sendTransaction(), 170000);
//     }

//     send_payment_reversal() {
//         this._super.apply(this, arguments);
//         console.log('send_payment_reversal');
//         // this.pos.get_order().selected_paymentline.set_payment_status('reversing');
//         // return this._sendTransaction(timapi.constants.TransactionType.reversal);
//     }

//     _sendTransaction (transactionType) {
//         let self = this;
//         console.log('_sendTransaction');
//         console.log(this.payment_method.neoleap_terminal_ip);
//         let ws;
//         try {
//             ws = new WebSocket(this.payment_method.neoleap_terminal_ip);
//             ws.addEventListener("close", (ev) => this._onSocketClose(ev, ws));
//             ws.addEventListener("error", (ev) => this._onSocketError(ev, ws));
//             ws.addEventListener("open", (ev) => this._onSocketOpen(ev, ws));
//             ws.addEventListener("message", (ev) => this._onSocketMessage(ev, ws));
//             this._ws = ws;
//         }
//         catch (error) {
//             this._ws = undefined;
//             console.log("WebSocket construction failed.");
//             return new Promise((resolve, reject) => { });
//         }
//         this.connectPromise = new Promise((resolve, reject) => {
//             this.transactionResolve = resolve;
//             this.transactionReject = reject;
//             this.connectTimeout = setTimeout(() => {
//                 console.log("Connect timed out. Exceeded time");
//                 ws.close(1000); // careful here to use a local reference instead of this._ws
//             }, 180000); // three minutes
//         }).finally(() => clearTimeout(this.connectTimeout));
//         return this.connectPromise;
//     }

//     _onSocketOpen(ev, ws) {
//         console.log('websocket opened');
//         let check = JSON.stringify({
//             "Command": "CHECK_STATUS"
//         });
//         console.log("checking device");
//         console.log("msg: ", check);
//         ws.send(check);
//     }

//     _onSocketError(ev, ws) {
//         console.log('websocket error');
//         console.log('event', ev);
//     }

//     _onSocketMessage(ev, ws) {
//         console.log('websocket message');
//         console.log('event1', ev);
//         console.log('ws1', ws);
//         if (ws !== this._ws) {
//             console.log('socket is not same instance');
//             return;
//         }
//         let data = false;
//         try {
//             data = JSON.parse(ev.data);
//         } catch { }
//         console.log(data);
//         console.log("typeof data: ", typeof (data));
//         if (data && typeof (data) === 'object') {
//             const { EventName } = data;
//             if (EventName === 'TERMINAL_STATUS') {
//                 const { TerminalStatus } = data;
//                 if (TerminalStatus === 'READY') {
//                     // SEND AMOUNT
//                     let lnAmount = this.pos.get_order().selected_paymentline.amount;
//                     let trxAmount = lnAmount.toFixed(2);
//                     let orderID = this.pos.get_order().uid;
//                     let msg = `{
//                     "Command": "SALE",
//                     "Amount": "${trxAmount}",
//                     "AdditionalData": "${orderID}"
//                 }`;
//                     console.log("sending payment request");
//                     console.log("msg: ", msg);
//                     ws.send(msg);
//                     // this.transactionResolve(true);
//                 }
//                 else {
//                     this.pos.get_order().selected_paymentline.set_payment_status('waiting');
//                     this.transactionReject(new Error('Terminal Busy'));
//                 }
//             }
//             if (EventName === 'TERMINAL_RESPONSE') {
//                 const { JsonResult } = data;
//                 if (JsonResult && JsonResult.StatusCode === "00") {
//                     // transaction approved
//                     let ecrReference = JsonResult.ECRReferenceNumber;
//                     let transactionAuthCode = JsonResult.TransactionAuthCode;
//                     this.pos.get_order().selected_paymentline.set_receipt_info(transactionAuthCode);
//                     this.pos.get_order().selected_paymentline.transaction_id = ecrReference;
//                     console.log('transaction approved');
//                     console.log('ecrReference: ', ecrReference);
//                     this.transactionResolve(true);
//                     this._ws.close(1000);
//                 }
//                 else if (JsonResult && JsonResult.StatusCode === "01") {
//                     // bank declined card
//                     this.transactionReject(new Error('Bank Decline'));
//                 } else if (JsonResult && JsonResult.StatusCode === "11") {
//                     // Cancelled transaction before capture
//                     this.pos.get_order().selected_paymentline.set_payment_status('waiting');
//                     this.transactionResolve(false);
//                     this._ws.close(1000);
//                 } else {
//                     Gui.showPopup('ErrorPopup', {
//                         title: _t('Transaction was not processed correctly'),
//                         body: JsonResult,
//                     });
//                     this.transactionResolve(false);
//                     this._ws.close(1000);
//                     // this.transactionReject(new Error('Unknown Error'));
//                 }
//             }
//         } else if (typeof (ev.data) === 'string') {
//             console.log("typeof data2: ", typeof (data));
//             let re_result_status = new RegExp(/<Result .*\/>/, "giu");
//             let re_approval_code = new RegExp(/<ApprovalCode(.*)\d+<\/ApprovalCode>/, "giu");
//             let result_tag = re_result_status.exec(ev.data);
//             let approval_tag = re_approval_code.exec(ev.data);
//             if (result_tag && approval_tag) {
//                 result_tag = result_tag[0];
//                 let result_status_code = result_tag.includes('APPROVED');
//                 if (!result_status_code) {
//                     Gui.showPopup('ErrorPopup', {
//                         title: _t('Transaction was not processed correctly'),
//                         body: JsonResult,
//                     });
//                     this.transactionResolve(false);
//                 }
//                 approval_tag = approval_tag[0];
//                 let re_approval_code = new RegExp(/\d+/, "g");
//                 let approval_code = re_approval_code.exec(approval_tag);
//                 if (!approval_code) {
//                     Gui.showPopup('ErrorPopup', {
//                         title: _t('Transaction was not processed correctly, '),
//                         body: JsonResult,
//                     });
//                     this.transactionResolve(false);
//                 }
//                 approval_code = approval_code[0];
//                 this.pos.get_order().selected_paymentline.set_receipt_info(approval_code);
//                 console.log('transaction approved');
//                 console.log('approval_code: ', approval_code);
//                 this.transactionResolve(true);
//             }
//         }

//     }

//     _onSocketClose(ev, ws) {
//         console.log('websocket close');
//         if (ws !== this._ws) {
//             return;
//         }
//         this._ws = undefined;
//     }

// }

// odoo.define('pos_neoleap.payment', function (require) {
//     "use strict";

//     const { Gui } = require('point_of_sale.Gui');
//     var core = require('web.core');
//     var PaymentInterface = require('point_of_sale.PaymentInterface');
//     var _t = core._t;

//     var PaymentNeoleap = PaymentInterface.extend({

//         /**
//          * @override
//          */
//         init: function () {
//             this._super.apply(this, arguments);
//             // this.enable_reversals();
//             console.log("I started to do something");
//             var terminal_ip = this.payment_method.neoleap_terminal_ip;
//             var instanced_payment_method = _.find(this.pos.payment_methods, function (payment_method) {
//                 return payment_method.use_payment_terminal === "neoleap"
//                     && payment_method.neoleap_terminal_ip === terminal_ip
//                     && payment_method.payment_terminal;
//             });
//             if (instanced_payment_method !== undefined) {
//                 var payment_terminal = instanced_payment_method.payment_terminal;
//                 this.terminal = payment_terminal.terminal;
//                 this.terminalListener = payment_terminal.terminalListener;
//                 return;
//             }
//         },

//         /**
//          * @override
//          */
//         send_payment_cancel: function () {
//             this._super.apply(this, arguments);
//             console.log('send_payment_cancel');
//             if (this._ws) {
//                 console.log('send_payment_cancel2');
//                 this._ws.close();
//             }
//             this.pos.get_order().selected_paymentline.set_payment_status('waiting');
//             try {
//                 this.transactionReject(new Error('Cancelled Payment'));
//             } catch { }
//             return Promise.resolve();
//         },

//         /**
//          * @override
//          */
//         send_payment_request: function (cid) {
//             let self = this;
//             this._super.apply(this, arguments);
//             console.log('send_payment_request');
//             let line = this.pos.get_order().selected_paymentline;
//             line.set_payment_status('waiting');
//             // return this._sendTransaction();
//             const timeout = (prom, time) => {
//                 let timer;
//                 return Promise.race([
//                     prom,
//                     new Promise((res, rej) => {
//                         timer = setTimeout(res, time)
//                     }).then((res) => {
//                         line.set_payment_status('force_done');
//                     })
//                 ]).finally(() => clearTimeout(timer));
//             }
//             return timeout(this._sendTransaction(), 170000);
//         },

//         /**
//          * @override
//         */
//         send_payment_reversal: function () {
//             this._super.apply(this, arguments);
//             console.log('send_payment_reversal');
//             // this.pos.get_order().selected_paymentline.set_payment_status('reversing');
//             // return this._sendTransaction(timapi.constants.TransactionType.reversal);
//         },

//         //--------------------------------------------------------------------------
//         // Private
//         //--------------------------------------------------------------------------

//         _sendTransaction: function (transactionType) {
//             let self = this;
//             console.log('_sendTransaction');
//             console.log(this.payment_method.neoleap_terminal_ip);
//             let ws;
//             try {
//                 ws = new WebSocket(this.payment_method.neoleap_terminal_ip);
//                 ws.addEventListener("close", (ev) => this._onSocketClose(ev, ws));
//                 ws.addEventListener("error", (ev) => this._onSocketError(ev, ws));
//                 ws.addEventListener("open", (ev) => this._onSocketOpen(ev, ws));
//                 ws.addEventListener("message", (ev) => this._onSocketMessage(ev, ws));
//                 this._ws = ws;
//             }
//             catch (error) {
//                 this._ws = undefined;
//                 console.log("WebSocket construction failed.");
//                 return new Promise((resolve, reject) => { });
//             }
//             this.connectPromise = new Promise((resolve, reject) => {
//                 this.transactionResolve = resolve;
//                 this.transactionReject = reject;
//                 this.connectTimeout = setTimeout(() => {
//                     console.log("Connect timed out. Exceeded time");
//                     ws.close(1000); // careful here to use a local reference instead of this._ws
//                 }, 180000); // three minutes
//             }).finally(() => clearTimeout(this.connectTimeout));
//             return this.connectPromise;
//         },
//         _onSocketOpen(ev, ws) {
//             console.log('websocket opened');
//             let check = JSON.stringify({
//                 "Command": "CHECK_STATUS"
//             });
//             console.log("checking device");
//             console.log("msg: ", check);
//             ws.send(check);
//         },
//         _onSocketError(ev, ws) {
//             console.log('websocket error');
//             console.log('event', ev);
//         },
//         _onSocketMessage(ev, ws) {
//             console.log('websocket message');
//             console.log('event1', ev);
//             console.log('ws1', ws);
//             if (ws !== this._ws) {
//                 console.log('socket is not same instance');
//                 return;
//             }
//             let data = false;
//             try {
//                 data = JSON.parse(ev.data);
//             } catch { }
//             console.log(data);
//             console.log("typeof data: ", typeof (data));
//             if (data && typeof (data) === 'object') {
//                 const { EventName } = data;
//                 if (EventName === 'TERMINAL_STATUS') {
//                     const { TerminalStatus } = data;
//                     if (TerminalStatus === 'READY') {
//                         // SEND AMOUNT
//                         let lnAmount = this.pos.get_order().selected_paymentline.amount;
//                         let trxAmount = lnAmount.toFixed(2);
//                         let orderID = this.pos.get_order().uid;
//                         let msg = `{
//                         "Command": "SALE",
//                         "Amount": "${trxAmount}",
//                         "AdditionalData": "${orderID}"
//                     }`;
//                         console.log("sending payment request");
//                         console.log("msg: ", msg);
//                         ws.send(msg);
//                         // this.transactionResolve(true);
//                     }
//                     else {
//                         this.pos.get_order().selected_paymentline.set_payment_status('waiting');
//                         this.transactionReject(new Error('Terminal Busy'));
//                     }
//                 }
//                 if (EventName === 'TERMINAL_RESPONSE') {
//                     const { JsonResult } = data;
//                     if (JsonResult && JsonResult.StatusCode === "00") {
//                         // transaction approved
//                         let ecrReference = JsonResult.ECRReferenceNumber;
//                         let transactionAuthCode = JsonResult.TransactionAuthCode;
//                         this.pos.get_order().selected_paymentline.set_receipt_info(transactionAuthCode);
//                         this.pos.get_order().selected_paymentline.transaction_id = ecrReference;
//                         console.log('transaction approved');
//                         console.log('ecrReference: ', ecrReference);
//                         this.transactionResolve(true);
//                         this._ws.close(1000);
//                     }
//                     else if (JsonResult && JsonResult.StatusCode === "01") {
//                         // bank declined card
//                         this.transactionReject(new Error('Bank Decline'));
//                     } else if (JsonResult && JsonResult.StatusCode === "11") {
//                         // Cancelled transaction before capture
//                         this.pos.get_order().selected_paymentline.set_payment_status('waiting');
//                         this.transactionResolve(false);
//                         this._ws.close(1000);
//                     } else {
//                         Gui.showPopup('ErrorPopup', {
//                             title: _t('Transaction was not processed correctly'),
//                             body: JsonResult,
//                         });
//                         this.transactionResolve(false);
//                         this._ws.close(1000);
//                         // this.transactionReject(new Error('Unknown Error'));
//                     }
//                 }
//             } else if (typeof (ev.data) === 'string') {
//                 console.log("typeof data2: ", typeof (data));
//                 let re_result_status = new RegExp(/<Result .*\/>/, "giu");
//                 let re_approval_code = new RegExp(/<ApprovalCode(.*)\d+<\/ApprovalCode>/, "giu");
//                 let result_tag = re_result_status.exec(ev.data);
//                 let approval_tag = re_approval_code.exec(ev.data);
//                 if (result_tag && approval_tag) {
//                     result_tag = result_tag[0];
//                     let result_status_code = result_tag.includes('APPROVED');
//                     if (!result_status_code) {
//                         Gui.showPopup('ErrorPopup', {
//                             title: _t('Transaction was not processed correctly'),
//                             body: JsonResult,
//                         });
//                         this.transactionResolve(false);
//                     }
//                     approval_tag = approval_tag[0];
//                     let re_approval_code = new RegExp(/\d+/, "g");
//                     let approval_code = re_approval_code.exec(approval_tag);
//                     if (!approval_code) {
//                         Gui.showPopup('ErrorPopup', {
//                             title: _t('Transaction was not processed correctly, '),
//                             body: JsonResult,
//                         });
//                         this.transactionResolve(false);
//                     }
//                     approval_code = approval_code[0];
//                     this.pos.get_order().selected_paymentline.set_receipt_info(approval_code);
//                     console.log('transaction approved');
//                     console.log('approval_code: ', approval_code);
//                     this.transactionResolve(true);
//                 }
//             }

//         },
//         _onSocketClose(ev, ws) {
//             console.log('websocket close');
//             if (ws !== this._ws) {
//                 return;
//             }
//             this._ws = undefined;
//         }
//     });

//     return PaymentNeoleap;

// });
