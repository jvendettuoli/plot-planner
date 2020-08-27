'use strict';

console.log('START Project subform.js');

//Cache common DOM elements
const $projRmvPlotBtn = $('.proj-rmv-plot-btn');
const $projRmvPlntlstBtn = $('.proj-rmv-plntlst-btn');
const $plotRmvPlntLstBtn = $('.plot-rmv-plntlst-btn');
// const $projectsForm = $('#add-projects-form');
// const $plotsForm = $('#add-plots-form');

const dataAttrProjectId = 'data-project-id';
const dataAttrPlotId = 'data-plot-id';
const dataAttrPlantListId = 'data-plantlist-id';

//Cache common DOM elements
const $toggleProjectsBtn = $('#toggle-projects-btn');
const $togglePlotsBtn = $('#toggle-plots-btn');
const $togglePlantlistsBtn = $('#toggle-plantlists-btn');
const $projectsForm = $('#add-projects-form');
const $plotsForm = $('#add-plots-form');
const $plantlistsForm = $('#add-plantlists-form');
const $plotList = $('#plot-list');
const $projectList = $('#project-list');
const $plantlistList = $('#plantlist-list');
const $modalBody = $('.modal-body');

function generateOptionHTML(value, text) {
	return `
	<option value="${value}">${text}</option>
	`;
}

$('ul').on('click', '.proj-rmv-plot-btn', function(evt) {
	const $li = $(evt.currentTarget).parent();
	const plotId = $(evt.currentTarget).parent().attr(dataAttrPlotId);
	const projectId = $li.attr(dataAttrProjectId);

	Connection.projectRemovePlot(projectId, plotId);
	$li.remove();
	console.log(generateOptionHTML(projectId, $li.text()));

	$('#plots').append(generateOptionHTML(plotId, $li.text()));
});

$('ul').on('click', '.proj-rmv-plntlst-btn', function(evt) {
	evt.preventDefault();
	const $li = $(evt.currentTarget).parent();
	const projectId = $li.attr(dataAttrProjectId);
	const plantlistId = $li.attr(dataAttrPlantListId);

	Connection.projectRemovePlantList(projectId, plantlistId);
	$li.remove();

	$('#plantlists').append(generateOptionHTML(plantlistId, $li.text()));
});

function generateLiHtml(element, projectId, elementId, elementName) {
	let rmvClass;
	if (element === 'project') {
		rmvClass = 'proj-rmv-plot-btn';
	}
	else if (element === 'plot') {
		rmvClass = 'plot-rmv-plntlst-btn';
	}
	else if (element === 'plantlist') {
		rmvClass = 'plot-rmv-plntlst-btn';
	}
	const li = `
	<li data-${element}-id=${elementId} data-project-id=${projectId}><a href="/${element}s/${elementId}">${elementName} </a><button class="btn btn-sm text-danger ${rmvClass}"> <i class="fas fa-times"></i></button></li>
	`;

	return li;
}

$togglePlotsBtn.click(function(evt) {
	$plotsForm.toggle('fast');
});
// $toggleProjectsBtn.click(function(evt) {
// 	$projectsForm.toggle('fast');
// });
$togglePlantlistsBtn.click(function(evt) {
	$plantlistsForm.toggle('fast');
});

// Handles Projects - Plots connections between subforms and connected lists
$plotsForm.submit(function(evt) {
	evt.preventDefault();

	// const plantlistId = $(evt.currentTarget).parent().attr(dataAttrPlantListId);
	const projectId = $(evt.currentTarget).parent().attr(dataAttrProjectId);
	let serializedInputs = $(this).serializeArray();

	// For each input, connect the project and plots, and update the Connected plots list and plots form to reflect the new connection.
	serializedInputs.forEach((element) => {
		if (element.name !== 'csrf_token') {
			Connection.projectAddPlot(projectId, element.value);
			const optionText = $(`option:selected[value='${element.value}']`).text();
			if ($projectList.text().includes('No plots connected yet.')) {
				$projectList.empty();
			}
			$projectList.append(generateLiHtml('plot', projectId, element.value, optionText));
			$(`option:selected[value='${element.value}']`).remove();
		}
	});
});

// Handles Projects - Plant List connections between subforms and connected lists
$plantlistsForm.submit(function(evt) {
	evt.preventDefault();
	console.log('PLOTFORM');

	const projectId = $(evt.currentTarget).parent().attr(dataAttrProjectId);

	let serializedInputs = $(this).serializeArray();

	// For each input, connect the plot and plantlist, and update the Connected Plots list and Plots form to reflect the new connection.
	serializedInputs.forEach((element) => {
		if (element.name !== 'csrf_token') {
			Connection.projectAddPlantList(projectId, element.value);
			const optionText = $(`option:selected[value='${element.value}']`).text();
			if ($plantlistList.text().includes('No plant lists connected yet.')) {
				$plantlistList.empty();
			}
			console.log(optionText);
			$plantlistList.append(generateLiHtml('plantlist', projectId, element.value, optionText));
			$(`option:selected[value='${element.value}']`).remove();
		}
	});
});
