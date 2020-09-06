'use strict';

console.log('START plotDesign.js');

const plotId = $('#add-forms').attr('data-plot-id');
const $plotContainer = $('.plot-cont');
const $plotCols = $('.plot-col');
const $plotRows = $('.plot-row');
const $selectAllBtn = $('#select-all-btn');
const $deselectAllBtn = $('#deselect-all-btn');
const $clearSelectedBtn = $('#clear-selected-btn');
const $rowSelects = $('.select-row');
const $colSelects = $('.select-col');

const $plantlistSelect = $('#plantlist-select');
const $plantSymbolTableBody = $('#plant-symbol-table').children('tbody');

const cellWidth = 50;
const rows = $plotRows.length;
const cols = $plotCols.length / rows;

function generateSymbolTrHtml(plpId, plant, symbol) {
	//Sets a default symbol if there is none.
	symbol = symbol || `<i class="symbol fas fa-seedling" style="color:#228B22;"></i>`;
	return `<tr>
				<td>
				${plant}
				</td>
				<td data-plp-id="${plpId}" class="text-center fa-2x">
				${symbol}
				</td>
			</tr>`;
}

$plotContainer.css('width', cellWidth * cols);

//Changes plants-symbols list based on selection of plantlists that have at least one plant.
$plantlistSelect.on('change', async function(evt) {
	console.log('select');
	console.log(evt);
	console.log($(this).val());
	const response = await Query.getPlantlistData($(this).val());
	const plantSymbolMap = response.plantlist_plants_symbols;

	//Put data on table
	console.log($plantSymbolTableBody);
	$plantSymbolTableBody.empty();
	for (let item of plantSymbolMap) {
		const td = generateSymbolTrHtml(item.plantlist_plants_id, item.plant_name, item.symbol);
		$plantSymbolTableBody.append(td);
	}
});

$deselectAllBtn.on('click', function(evt) {
	console.log($plotCols);

	for (const cell of $plotCols) {
		const $cell = $(cell);
		if ($cell.hasClass('selected')) {
			$cell.removeClass('selected');
		}
	}
	$colSelects.removeClass('remove');
	$colSelects.addClass('add');
	$rowSelects.removeClass('remove');
	$rowSelects.addClass('add');
});
$selectAllBtn.on('click', function(evt) {
	console.log($plotCols);

	for (const cell of $plotCols) {
		const $cell = $(cell);
		if (!$cell.hasClass('selected')) {
			$cell.addClass('selected');
		}
	}
	$colSelects.removeClass('add');
	$colSelects.addClass('remove');
	$rowSelects.removeClass('add');
	$rowSelects.addClass('remove');
});
$clearSelectedBtn.on('click', async function(evt) {
	console.log($plotCols.filter('.selected'));

	for (const cell of $plotCols.filter('.selected')) {
		const $cell = $(cell);
		if ($cell.html().includes('symbol')) {
			$cell.empty();
			const cellX = $cell.attr('data-col');
			const cellY = $cell.attr('data-row');
			await Connection.plotCellDeleteSymbol(plotId, cellX, cellY);
		}
	}
});

$plotContainer.on('click', '.select-row', function(evt) {
	const $selectRow = $(evt.currentTarget);

	if ($selectRow.hasClass('add')) {
		$selectRow.siblings('div').addClass('selected');
	}
	else {
		$selectRow.siblings('div').removeClass('selected');
	}
	$selectRow.toggleClass('add');
	$selectRow.toggleClass('remove');
});

$plotContainer.on('click', '.select-col', function(evt) {
	const $selectCol = $(evt.currentTarget);
	const col = $selectCol.attr('data-col');

	if ($selectCol.hasClass('add')) {
		$(`.plot-col[data-col=${col}]`).addClass('selected');
	}
	else {
		$(`.plot-col[data-col=${col}]`).removeClass('selected');
	}

	$selectCol.toggleClass('add');
	$selectCol.toggleClass('remove');
});
$plotContainer.on('click', '.plot-col', function(evt) {
	console.log(evt);
	$(evt.currentTarget).toggleClass('selected');
});

$plantSymbolTableBody.on('click', '.symbol', function(evt) {
	const $symbol = $(evt.currentTarget).clone();
	const plantlistsPlantsId = $(evt.currentTarget).parent().attr('data-plp-id');
	console.log(plantlistsPlantsId);
	$('.selected').html($symbol);
	// $('.selected').attr('data-plp-id', plantlistsPlantsId);

	//save symbol
	for (let cell of $('.selected')) {
		const $cell = $(cell);
		console.log($cell.attr('data-row'));
		const cellX = $cell.attr('data-col');
		const cellY = $cell.attr('data-row');
		Connection.plotCellAddSymbol(plotId, cellX, cellY, plantlistsPlantsId);
	}
});

async function drawPlotSymbols() {
	const plotSymbols = await Query.getPlotCellSymbols(plotId);
	plotSymbols.forEach((ele) => {
		const $cell = $(`[data-col=${ele.cell_x}][data-row=${ele.cell_y}]`);
		$cell.html(ele.symbol);
	});
}

drawPlotSymbols();
