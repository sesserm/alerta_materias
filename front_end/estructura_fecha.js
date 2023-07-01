// Afecta el display de la fecha en el front principal

var selects = document.getElementsByTagName('select');
for (var i = 0; i < selects.length; i++) {
    selects[i].addEventListener('change', function() {
        var selectedOption = this.options[this.selectedIndex];
        var selectedDate = selectedOption.value;
        var datesContainer = this.parentNode.querySelector('.dates-list');
        var expandableIcon = this.parentNode.querySelector('.expandable');
        expandableIcon.textContent = selectedDate;
        datesContainer.classList.add('hidden');
        });
    selects[i].addEventListener('click', function(event) {
        var datesContainer = this.parentNode.querySelector('.dates-list');
        datesContainer.classList.toggle('hidden');
        event.stopPropagation();
        });
    selects[i].addEventListener('focus', function(event) {
        var fechaList = Array.from(this.options).map(function(option) {
            return option.value;
            });
        fechaList.sort(function(a, b) {
            return new Date(a) - new Date(b);
            });
        var selectedDate = this.value;
        this.innerHTML = '';
        for (var j = 0; j < fechaList.length; j++) {
            var option = document.createElement('option');
            option.value = fechaList[j];
            option.textContent = fechaList[j];
            this.appendChild(option);
            }
        this.value = selectedDate;
        });
    }
var datesContainers = document.getElementsByClassName('dates-list');
for (var i = 0; i < datesContainers.length; i++) {
    var datesContainer = datesContainers[i];
    if (datesContainer.innerHTML.trim() === '') {
        datesContainer.innerHTML = 'SIN DATO';
        }
    }