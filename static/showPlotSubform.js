'use strict';

console.log('START Plotsubform.js');

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

	$('#projects').append(generateOptionHTML(projectId, $li.text()));
});

$('ul').on('click', '.plot-rmv-plntlst-btn', function(evt) {
	evt.preventDefault();
	const $li = $(evt.currentTarget).parent();
	const plotId = $li.attr(dataAttrPlotId);
	const plantlistId = $li.attr(dataAttrPlantListId);

	Connection.plotRemovePlantList(plotId, plantlistId);
	$li.remove();

	$('#plantlists').append(generateOptionHTML(plantlistId, $li.text()));

	//Remove the option from the Plot Design plantlist select
	$plantlistSelect.children(`[value="${plantlistId}"]`).remove();
});

function generateLiHtml(element, plotId, elementId, elementName) {
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
	<li data-${element}-id=${elementId} data-plot-id=${plotId}><a href="/${element}s/${elementId}">${elementName} </a><button class="btn btn-sm text-danger ${rmvClass}"> <i class="fas fa-times"></i></button></li>
	`;

	return li;
}

// $togglePlotsBtn.click(function(evt) {
// 	$plotsForm.toggle('fast');
// });
$toggleProjectsBtn.click(function(evt) {
	$projectsForm.toggle('fast');
});
$togglePlantlistsBtn.click(function(evt) {
	$plantlistsForm.toggle('fast');
});

// Handles Projects - Plotsconnections between subforms and connected lists
$projectsForm.submit(function(evt) {
	evt.preventDefault();

	// const plantlistId = $(evt.currentTarget).parent().attr(dataAttrPlantListId);
	const plotId = $(evt.currentTarget).closest('[data-plot-id]').attr(dataAttrPlotId);
	let serializedInputs = $(this).serializeArray();

	// For each input, connect the project and plantlist, and update the Connected Projects list and Projects form to reflect the new connection.
	serializedInputs.forEach((element) => {
		if (element.name !== 'csrf_token') {
			Connection.projectAddPlot(element.value, plotId);
			const optionText = $(`option:selected[value='${element.value}']`).text();
			if ($projectList.text().includes('No projects connected yet.')) {
				$projectList.empty();
			}
			$projectList.append(generateLiHtml('project', plotId, element.value, optionText));
			$(`option:selected[value='${element.value}']`).remove();
		}
	});
});

// Handles Plots - Plant List connections between subforms and connected lists
$plantlistsForm.submit(function(evt) {
	evt.preventDefault();
	console.log('PLOTFORM');

	const plotId = $(evt.currentTarget).closest('[data-plot-id]').attr(dataAttrPlotId);

	let serializedInputs = $(this).serializeArray();

	// For each input, connect the plot and plantlist, and update the Connected Plots list and Plots form to reflect the new connection.
	serializedInputs.forEach((element) => {
		if (element.name !== 'csrf_token') {
			Connection.plotAddPlantList(plotId, element.value);
			const optionText = $(`option:selected[value='${element.value}']`).text();
			if ($plantlistList.text().includes('No plant lists connected yet.')) {
				$plantlistList.empty();
			}
			console.log(optionText);
			$plantlistList.append(generateLiHtml('plantlist', plotId, element.value, optionText));
			$(`option:selected[value='${element.value}']`).remove();

			//remove from Plot Design Plantlist Select list
			$plantlistSelect.append(generateOptionHTML(element.value, optionText));
		}
	});
});
