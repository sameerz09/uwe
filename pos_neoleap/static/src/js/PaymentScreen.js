// odoo.define('pos_neoleap.PaymentScreen', function (require) {
//     'use strict';

//     const { _t } = require('web.core');
//     const PaymentScreen = require('point_of_sale.PaymentScreen');
//     const Registries = require('point_of_sale.Registries');
//     const NumberBuffer = require('point_of_sale.NumberBuffer');
//     const { useBarcodeReader } = require('point_of_sale.custom_hooks');
//     const { useListener } = require("@web/core/utils/hooks");



//     const PosNeoleapPaymentScreen = (PaymentScreen) =>
//         class extends PaymentScreen {

//             setup() {
//                 super.setup();
//                 useListener('handle-payment-manually', this._handle_payment_manually);

//             }

//             async _handle_payment_manually() {
//                 const {
//                     confirmed,
//                     payload
//                 } = await this.showPopup('ReferencePopup', {
//                     title: this.env._t('Approval Number'),
//                     startingValue: null,
//                 });
//                 if (!confirmed) return false;
//                 if (confirmed) {
//                     if (payload != null && payload.length >= 6) {
//                         console.log("Payload: ", payload);
//                         this.currentOrder.selected_paymentline.set_receipt_info(payload);
//                         this.currentOrder.selected_paymentline.set_payment_status('force_done');
//                     } else {
//                         await this.showPopup('ErrorPopup', {
//                             title: 'Card Payment Reference Is Required',
//                             body: 'Must be greater than 6 inputs and on a different sequence. \n رقم الكي نت يجب الا يقل عن 6 ارقام',
//                         });
//                         return false;
//                     }
//                 }
//             }

//             deletePaymentLine(event) {
//                 console.log("deletePaymentLine");
//                 const { cid } = event.detail;
//                 const line = this.paymentLines.find((line) => line.cid === cid);
//                 console.log("deletePaymentLine2 line", line.payment_method);
//                 if (line.get_payment_status() === 'waitingCancel') {
//                     this.currentOrder.remove_paymentline(line);
//                     NumberBuffer.reset();
//                     this.render(true);
//                 }
//                 return super.deletePaymentLine(event);
//             }
//         };


//     Registries.Component.extend(PaymentScreen, PosNeoleapPaymentScreen);

//     return PaymentScreen;

// });