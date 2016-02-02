var IpReportLossPage = function () {};

IpReportLossPage.prototype = Object.create({}, {

    visit: {
        value: function (itemId) {
            browser.get('/#/deliveries-by-ip/' + itemId + '/report-loss');
        }
    },

    itemName: {
        get: function () {
            return element(by.id('itemNameLabel')).getText();
        }
    },
    //
    //itemAvailableQty: {
    //    get: function () {
    //        return element(by.id('qty-available-label')).getText();
    //    }
    //}
});

module.exports = new IpReportLossPage;