'use strict';

console.log('START plotDesign.js');

const $plotContainer = $('.plot-design');
const $plotCols = $('.plot-col');
const $plotRows = $('.plot-row');

const $plantlistSelect = $('#plantlist-select');
const $plantSymbolTableBody = $('#plant-symbol-table').children('tbody');

const cellWidth = 50;
const rows = $plotRows.length;
const cols = $plotCols.length / rows;

function generateSymbolTrHtml(plant, symbol) {
	symbol = symbol || `<i class="symbol fas fa-seedling" style="color:#228B22;"></i>`;
	return `<tr>
				<td>
				${plant}
				</td>
				<td class="text-center fa-2x">
				${symbol}
				</td>
			</tr>`;
}

$plotContainer.css('width', cellWidth * cols);

$plantlistSelect.on('change', async function(evt) {
	console.log('select');
	console.log(evt);
	console.log($(this).val());
	const response = await Query.getPlantlistData($(this).val());
	const plants = response.plants;
	const plantSymbolMap = response.plant_symbol_map;
	//Put data on table
	console.log($plantSymbolTableBody);
	$plantSymbolTableBody.empty();
	for (let plant of plants) {
		const td = generateSymbolTrHtml(plant, plantSymbolMap[`${plant}`]);
		$plantSymbolTableBody.append(td);
	}
});
