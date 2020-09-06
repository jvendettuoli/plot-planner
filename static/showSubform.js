'use strict';

console.log('START subform.js');

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
const $projectsForm = $('#add-projects-form');
const $plotsForm = $('#add-plots-form');
const $plotList = $('#plot-list');
const $projectList = $('#project-list');
const $modalBody = $('.modal-body');

function generateOptionHTML(value, text) {
	return `
	<option value="${value}">${text}</option>
	`;
}

$projRmvPlotBtn.click(function(evt) {
	const plotId = $(evt.currentTarget).parent().attr(dataAttrPlotId);
	const projectId = $(evt.currentTarget).parent().attr(dataAttrProjectId);

	Connection.projectRemovePlot(projectId, plotId);
	$(evt.currentTarget).parent().remove();
});

$('ul').on('click', '.proj-rmv-plntlst-btn', function(evt) {
	const $li = $(evt.currentTarget).parent();
	const plantlistId = $li.attr(dataAttrPlantListId);
	const projectId = $li.attr(dataAttrProjectId);

	Connection.projectRemovePlantList(projectId, plantlistId);
	$li.remove();

	$('#projects').append(generateOptionHTML(projectId, $li.text()));
});

$('ul').on('click', '.plot-rmv-plntlst-btn', function(evt) {
	evt.preventDefault();
	const $li = $(evt.currentTarget).parent();
	const plantlistId = $li.attr(dataAttrPlantListId);
	const plotId = $li.attr(dataAttrPlotId);

	Connection.plotRemovePlantList(plotId, plantlistId);
	$li.remove();

	$('#plots').append(generateOptionHTML(plotId, $li.text()));
});

function generateLiHtml(element, plantlistId, elementId, elementName) {
	let rmvClass;
	if (element === 'project') {
		rmvClass = 'proj-rmv-plntlst-btn';
	}
	else if (element === 'plot') {
		rmvClass = 'plot-rmv-plntlst-btn';
	}
	const li = `
	<li data-${element}-id=${elementId} data-plantlist-id=${plantlistId}><a href="/${element}s/${elementId}">${elementName} </a><button class="btn btn-sm text-danger ${rmvClass}"> <i class="fas fa-times"></i></button></li>
	`;

	return li;
}

$togglePlotsBtn.click(function(evt) {
	$plotsForm.toggle('fast');
});
$toggleProjectsBtn.click(function(evt) {
	$projectsForm.toggle('fast');
});

// Handles Projects - Plant Lists connections between subforms and connected lists
$projectsForm.submit(function(evt) {
	evt.preventDefault();

	const plantlistId = $(evt.currentTarget).closest('[data-plantlist-id]').attr(dataAttrPlantListId);
	let serializedInputs = $(this).serializeArray();

	// For each input, connect the project and plantlist, and update the Connected Projects list and Projects form to reflect the new connection.
	serializedInputs.forEach((element) => {
		if (element.name !== 'csrf_token') {
			Connection.projectAddPlantList(element.value, plantlistId);
			const optionText = $(`option:selected[value='${element.value}']`).text();
			if ($projectList.text().includes('No projects connected yet.')) {
				$projectList.empty();
			}
			$projectList.append(generateLiHtml('project', plantlistId, element.value, optionText));
			$(`option:selected[value='${element.value}']`).remove();
		}
	});
});
// Handles Projects - Plot connections between subforms and connected lists

// $modalBody.on('submit', function(evt) {
// 	evt.preventDefault();
// 	console.log('Proj-PLOTFORM');
// 	console.log('event', evt);

// 	const projectId = $(evt.currentTarget).attr(dataAttrProjectId);
// 	console.log('evet target', evt.currentTarget);
// 	console.log('ProjectID', projectId);
// 	let serializedInputs = $(this).children('form').serializeArray();
// 	console.log(serializedInputs);

// 	// For each input, connect the plot and plantlist, and update the Connected Plots list and Plots form to reflect the new connection.
// 	serializedInputs.forEach((element) => {
// 		if (element.name !== 'csrf_token') {
// 			Connection.projectAddPlot(projectId, element.value);
// 			const optionText = $(`option:selected[value='${element.value}']`).text();
// 			if ($plotList.text().includes('No plots connected yet.')) {
// 				$plotList.empty();
// 			}
// 			console.log($(`#plot-list-${projectId}`));
// 			$(`#plot-list-${projectId}`).append(generateLiHtml('plot', projectId, element.value, optionText));
// 			$(`option:selected[value='${element.value}']`).remove();
// 		}
// 	});
// });

// Handles Plots - Plant List connections between subforms and connected lists
$plotsForm.submit(function(evt) {
	evt.preventDefault();
	console.log('PLOTFORM');

	const plantlistId = $(evt.currentTarget).closest('[data-plantlist-id]').attr(dataAttrPlantListId);
	let serializedInputs = $(this).serializeArray();

	// For each input, connect the plot and plantlist, and update the Connected Plots list and Plots form to reflect the new connection.
	serializedInputs.forEach((element) => {
		if (element.name !== 'csrf_token') {
			Connection.plotAddPlantList(element.value, plantlistId);
			const optionText = $(`option:selected[value='${element.value}']`).text();
			if ($plotList.text().includes('No plots connected yet.')) {
				$plotList.empty();
			}
			$plotList.append(generateLiHtml('plot', plantlistId, element.value, optionText));
			$(`option:selected[value='${element.value}']`).remove();
		}
	});
});
