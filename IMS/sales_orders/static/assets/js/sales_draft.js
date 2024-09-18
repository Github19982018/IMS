form = document.querySelector('#sales_draft') 
document.querySelector('#datein').value = new Date().toLocaleString()
document.querySelector('#total').textContent = Number(document.querySelector('#sub').textContent) + Number(document.querySelector('#discount').val);
// form.addEventListener('submit',(e) => {
// e.preventDefault()
// fetch(location.host+'/ims/v1/sales/save',{
//     method:'post',
//     body :{
//         'total_price':document.querySelector('#total'),
//         'offer':document.querySelector('#discount')
//     }
// })
// form.submit()
// })

window.addEventListener('beforeunload', function(e) {
    this.alert("Are you sure to leave? All changes will be lost.")
    e.preventDefault()
    return ("Are you sure to leave? All changes will be lost.")
})


function add_items(items, extra=0){
    let sum = 0
    for( i of items){
        sum += (i.quantity*i.price)-(i.quantity*i.price*i.discount/100)
        sum += extra 
    }
    return sum
}

function price_calc(){
    document.querySelector('#total').textContent=this.value*document.querySelector('#price').textContent;
    items = document.querySelectorAll('.total')
    var total = 0;
    for(i of items){
        total += Number(i.textContent)
    }
    document.querySelector('#sub').textContent = total
    document.querySelector('#total_amount').textContent = total - document.querySelector('#offer').textContent 
}

function offer_calc(){
    tot = document.querySelector('#sub').textContent;
    document.querySelector('#total_amount').textContent = tot - document.querySelector('#offer').textContent ;
}
