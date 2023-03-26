// add hovered class to selected list item
let list = document.querySelectorAll(".navigation li");

function activeLink() {
	list.forEach((item) => {
    item.classList.remove("hovered");
});
	this.classList.add("hovered");
}

list.forEach((item) => item.addEventListener("mouseover", activeLink));

// Menu Toggle
let toggle = document.querySelector(".toggle");
let navigation = document.querySelector(".navigation");
let main = document.querySelector(".main");

toggle.onclick = function () {
	navigation.classList.toggle("active");
	main.classList.toggle("active");
};

// Add room //
var app = angular.module('firstApp', [])

//information in this controller will be bound to itself using vm
app.controller('mainController', function(){

	//It is a good practice to bind the parent this in the controller to vm
	//bind this to vm (view-model)
	var vm = this;

	//define variables and objects on this
	//this lets them be available to our views

	//define a list of items
	vm.roomList = [
	{name: 'จอ',},
	{name: 'กระดาน',},
	{name: 'โต๊ะ'}
	];

	//information that comes from our form
	vm.roomData = {};

	vm.addItem = function(){

		//add a grocery to the list
		vm.roomList.push({
			name: vm.roomData.name,
		});

		//after our grocery has been added, clean the form
		vm.roomData = {};
	};
});
