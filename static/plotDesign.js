'use strict';

// commonly used DOM elements and plot id
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

// Sets standard plot cell width and gets rows and cols values
const cellWidth = 50;
const rows = $plotRows.length;
const cols = $plotCols.length / rows;

// Generates HTML for the plant symbol table. plpId = plantlist_plant_id
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

// Sets the width of the plot container for style purposes
$plotContainer.css('width', cellWidth * cols);

//Changes plants-symbols list based on selection of plantlists that have at least one plant.
$plantlistSelect.on('change', handlePlantlistSelect);

$deselectAllBtn.on('click', handleDeselectAll);
$selectAllBtn.on('click', handleSelectAll);
$clearSelectedBtn.on('click', handleClearSelected);

// Handler for click on any of the row select cells
$plotContainer.on('click', '.select-row', handleSelectRow);
// Handler for click on any of the column select cells
$plotContainer.on('click', '.select-col', handleSelectCol);
// On click of any plot cell this toggles selected class
$plotContainer.on('click', '.plot-col', function(evt) {
	$(evt.currentTarget).toggleClass('selected');
});
// On click of any symbol on the plant-symbol table applies that
// symbol to selected cells
$plantSymbolTableBody.on('click', '.symbol', handleSymbolSelect);

// gets plants - symbols and populates plant - symbol table
async function handlePlantlistSelect(evt) {
	const response = await Query.getPlantlistData($(this).val());
	const plantSymbolMap = response.plantlist_plants_symbols;

	//Put data on table
	$plantSymbolTableBody.empty();
	for (let item of plantSymbolMap) {
		const td = generateSymbolTrHtml(item.plantlist_plants_id, item.plant_name, item.symbol);
		$plantSymbolTableBody.append(td);
	}
}

// On click of Deselect All btn, clears all selected class from all cells
// Also resets all col and row selects to initial state
function handleDeselectAll(evt) {
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
}

// On call adds selected class to all cells and sets col and row
// select btns to remove state
function handleSelectAll(evt) {
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
}

// On call removes symbols from any selected cells
// also removes connection in database
async function handleClearSelected(evt) {
	for (const cell of $plotCols.filter('.selected')) {
		const $cell = $(cell);
		if ($cell.html().includes('symbol')) {
			$cell.empty();
			const cellX = $cell.attr('data-col');
			const cellY = $cell.attr('data-row');
			await Connection.plotCellDeleteSymbol(plotId, cellX, cellY);
		}
	}
}

// Selects a full row of cells
function handleSelectRow(evt) {
	const $selectRow = $(evt.currentTarget);
	if ($selectRow.hasClass('add')) {
		$selectRow.siblings('div').addClass('selected');
	}
	else {
		$selectRow.siblings('div').removeClass('selected');
	}
	$selectRow.toggleClass('add');
	$selectRow.toggleClass('remove');
}

// Selects a full column of cells
function handleSelectCol(evt) {
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
}

// Clones selected symbol and applies to selected cells
// Also saves connection of cell to symbol in database
function handleSymbolSelect(evt) {
	const $symbol = $(evt.currentTarget).clone();
	const plantlistsPlantsId = $(evt.currentTarget).parent().attr('data-plp-id');
	$('.selected').html($symbol);

	//save symbol
	for (let cell of $('.selected')) {
		const $cell = $(cell);
		const cellX = $cell.attr('data-col');
		const cellY = $cell.attr('data-row');
		Connection.plotCellAddSymbol(plotId, cellX, cellY, plantlistsPlantsId);
	}
}

// Gets the symbols for each plot cell and displays them.
async function drawPlotSymbols() {
	const plotSymbols = await Query.getPlotCellSymbols(plotId);
	plotSymbols.forEach((ele) => {
		const $cell = $(`[data-col=${ele.cell_x}][data-row=${ele.cell_y}]`);
		$cell.html(ele.symbol);
	});
}

// Applies current plot symbols on page load
$(drawPlotSymbols());
