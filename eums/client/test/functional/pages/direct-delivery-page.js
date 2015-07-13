var DirectDeliveryPage = function () {};

DirectDeliveryPage.prototype = Object.create({}, {
    url: { get: function () { return '#/direct-delivery'; }},

    visit: { value: function () {
        browser.get(this.url);
        var EC = protractor.ExpectedConditions;
        var fadingModal = element(by.css('.modal-backdrop.fade'));
        var ordersHaveLoaded = EC.stalenessOf(fadingModal);
        browser.wait(ordersHaveLoaded, 5000, "Timeout exceeded while loading purchase orders");
    }},

    purchaseOrders: { get: function () { return element.all(by.repeater('purchaseOrder in purchaseOrders').column('purchaseOrder.orderNumber')).getText(); }},
    purchaseOrderCount: { get: function () { return element.all(by.repeater('purchaseOrder in purchaseOrders')).count(); }},

    selectPurchaseOrderByNumber: { value: function (text) { element(by.linkText(text)).click(); }},
    selectSingleIP: { value: function () { element(by.id('single-ip')).click(); }},
    selectMultipleIP: { value: function () { element(by.id('multiple-ip')).click(); }},

    purchaseOrderItems: { get: function () { return element.all(by.repeater('(index, item) in purchaseOrderItems').column('item.display')).getText(); }},
    purchaseOrderQuantities: { get: function () { return element.all(by.repeater('(index, item) in purchaseOrderItems').column('item.quantity')).getText(); }},
    purchaseOrderValues: { get: function () { return element.all(by.repeater('(index, item) in purchaseOrderItems').column('item.value')).getText(); }},

    searchBar: { get:  function () { return element(by.id('filter')); }},
    searchForThisPurchaseOrder: { value: function (searchTerm) {
        this.searchBar.clear().sendKeys(searchTerm);
    }}
});

module.exports = new DirectDeliveryPage;
