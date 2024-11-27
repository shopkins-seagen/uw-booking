function toggleActions(element) {
    if (element.value == 0) {
        document.getElementById("div_controls").style.pointerEvents = "none";
    } else {
        document.getElementById("div_controls").style.pointerEvents = "all";
    }
}

function addCustomer() {
    window.location.href = "/customer";
}

function editCustomer(id) {
    window.location.href = "/edit/" + id;
}

function cancel() {
    window.location.href = '/';
}

function addOrder() {
    let id = document.getElementById("customer").value;
    window.location.href = "/order/" + id;
}

function validateOrder(v, w) {
    let vol = parseFloat(v);
    let wt = parseFloat(w);

    if (vol * wt === 0 || vol + wt <= 0) {
        alert("Volume and Weight must be greater than zero");
        return false;
    }
    if (vol >= 125 && wt >= 10) {
        alert("Item exceeds capacity. Weight must be under 10kg or Volume must be 125m^3 or less");
        return false;
    }
    return true;
}

function isUrgent() {
    let urgent = document.getElementById("urgent");
    let today = new Date();
    let days = Math.ceil((Date.parse(document.getElementById("deliver_by").value) - today) / (1000 * 3600 * 24));
    urgent.style.display = days <= 3 ? "block" : "none";
}

function deleteCustomer(id, name) {
    if (confirm('Are you sure you want to delete ' + name + '?') == true) {
        window.location.href = '/delete/' + id;
    } else {
        return false;
    }
}

$(document).ready(function () {
    if (document.URL.match('confirmation') != null) {

        document.getElementById("is_global").style.display =  document.getElementById("is_global_value").value === "True" ? "block" : "none";
        document.getElementById("is_urgent").style.display = document.getElementById("is_urgent_value").value === "True" ? "block" : "none";
        document.getElementById("is_hazard").style.display = document.getElementById("is_hazard_value").value=== "True" ? "block" : "none";
    }
});

function enabledQuote(quotes) {
    if (quotes===null) {
        alert("No shipping options available. set the date");
        return false;
    }
    return true;
}