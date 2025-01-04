// odoo.define('pos_neoleap.chrome', function (require) {
//     'use strict';

//     const Chrome = require('point_of_sale.Chrome');
//     const Registries = require('point_of_sale.Registries');

//     const PosNeoleapChrome = (Chrome) =>
//         class extends Chrome {
//             get balanceButtonIsShown() {
//                 return this.env.pos.payment_methods.some(pm => pm.use_payment_terminal === 'neoleap');
//             }
//         };

//     Registries.Component.extend(Chrome, PosNeoleapChrome);

//     return Chrome;
// });
