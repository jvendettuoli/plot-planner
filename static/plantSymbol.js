'use strict';
console.log('START plantSymbol.js');

const $plantSymbol = $('.symbol');
const $plantSymbolPreview = $('#symbol-preview');
const $colorInput = $('#symbol-color-input');
// const $addSymbolBtn = $('.btn.add-symbol');
const $createSymbolBtn = $('#create-symbol-btn');
// const $editSymbolBtn = $('.badge.edit-symbol');

const editBtnHTM = `<h5><span class="badge badge-success edit-symbol open-symbol-modal" style="cursor: pointer;" data-toggle="modal" data-target="#symbolModal">Edit</span></h5>`;

let $customSymbolCont;

class Symbol {
	constructor() {
		//Change out based on deployment
		this.baseURL = 'http://127.0.0.1:5000';
	}
	//Change out based on deployment
	static baseUrl = 'http://127.0.0.1:5000';

	//GET request to get connections based on a primaryId and secondary type
	static async addSymbol(symbol, plantlistId, plantId) {
		const res = await axios.post(`${this.baseUrl}/plantlists/${plantlistId}/plant/${plantId}/symbol/add`, {
			symbol
		});

		console.log(res);
		console.log(res.data);
	}
}

$plantSymbol.on('click', function(evt) {
	console.log('Click');
	const $selectedSymbol = $(evt.currentTarget).clone().removeClass('fa-2x');
	console.log('SELECTED', $selectedSymbol);

	$plantSymbolPreview.html($selectedSymbol);
});

$colorInput.on('change', function() {
	console.log('INPUT');
	const selectedColor = $(this).val();
	$plantSymbolPreview.attr('style', `color: ${selectedColor}`);
});

$createSymbolBtn.on('click', function() {
	console.log('CREATER CLICk');

	const styleColor = $plantSymbolPreview.attr('style');
	const $createdSymbol = $plantSymbolPreview.children('i').clone();
	$createdSymbol.attr('style', `${styleColor}`);

	$customSymbolCont.children('#symbol-display').html($createdSymbol);

	const plantlistId = $customSymbolCont.attr('data-plantlist-id');
	const plantId = $customSymbolCont.attr('data-plant-id');

	console.log($customSymbolCont.children('#change-symbol-btn'));

	$customSymbolCont.children('#change-symbol-btn').html(editBtnHTM);
	Symbol.addSymbol($createdSymbol.clone()[0].outerHTML, plantlistId, plantId);
});

$('td').on('click', '.open-symbol-modal', function(evt) {
	console.log('click');
	console.log($(evt.currentTarget).closest('.custom-symbol-cont'));
	$customSymbolCont = $(evt.currentTarget).closest('.custom-symbol-cont');
});
