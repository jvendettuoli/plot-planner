'use strict';

console.log('START plotDesign.js');

const $plotContainer = $('.plot-design');
const $plotCols = $('.plot-col');
const $plotRows = $('.plot-row');

const cellWidth = 50;
const rows = $plotRows.length;
const cols = $plotCols.length / rows;

$plotContainer.css('width', cellWidth * cols);
