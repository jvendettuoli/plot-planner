'use strict';

const $plantSymbol = $('.symbol');
const $plantSymbolPreview = $('#symbol-preview');
const $colorInput = $('#symbol-color-input');
const $createSymbolBtn = $('#create-symbol-btn');

const editBtnHTM = `<h5><span class="badge badge-info edit-symbol open-symbol-modal" style="cursor: pointer;" data-toggle="modal" data-target="#symbolModal">Edit</span></h5>`;

let $customSymbolCont;

// Symbo Class
class Symbol {
	constructor() {
		//Change out based on deployment
		this.baseURL = 'https://plot-planner.herokuapp.com';
	}
	//Change out based on deployment
	static baseUrl = 'https://plot-planner.herokuapp.com';

	//POST request to add symbol to plant of a given plantlist
	static async addSymbol(symbol, plantlistId, plantId) {
		const res = await axios.post(`${this.baseUrl}/plantlists/${plantlistId}/plant/${plantId}/symbol/add`, {
			symbol
		});
	}
	// Strips size class from symbol and applies symbol to preview area
	static previewSymbol(evt) {
		const $selectedSymbol = $(evt.currentTarget).clone().removeClass('fa-2x');
		$plantSymbolPreview.html($selectedSymbol);
	}

	static changeColor() {
		const selectedColor = $(this).val();
		$plantSymbolPreview.attr('style', `color: ${selectedColor}`);
	}

	// Clones symbol and applys color based on preview symbol and
	// applies that symbol to the approriate plant.
	// Adds the symbol to the database and connects it to the plant
	static applySymbol() {
		const styleColor = $plantSymbolPreview.attr('style');
		const $createdSymbol = $plantSymbolPreview.children('i').clone();
		$createdSymbol.attr('style', `${styleColor}`);
		$customSymbolCont.children('#symbol-display').html($createdSymbol);
		const plantlistId = $customSymbolCont.attr('data-plantlist-id');
		const plantId = $customSymbolCont.attr('data-plant-id');
		$customSymbolCont.children('#change-symbol-btn').html(editBtnHTM);
		Symbol.addSymbol($createdSymbol.clone()[0].outerHTML, plantlistId, plantId);
	}

	static setTarget(evt) {
		$customSymbolCont = $(evt.currentTarget).closest('.custom-symbol-cont');
	}
}

// On click of a symbol in the symbol creation modal
$plantSymbol.on('click', Symbol.previewSymbol);
// On color input change, applies color to preview symbol
$colorInput.on('change', Symbol.changeColor);
// On click of Create Btn, save preview symbol to custom symbol container
// and add symbol to database
$createSymbolBtn.on('click', Symbol.applySymbol);
// On click of add or edit btn sets which symbol is being updated
$('td').on('click', '.open-symbol-modal', Symbol.setTarget);
