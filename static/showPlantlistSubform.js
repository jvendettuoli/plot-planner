'use strict';

// Set common strings to variables
const dataAttrProjectId = 'data-project-id';
const dataAttrPlotId = 'data-plot-id';
const dataAttrPlantListId = 'data-plantlist-id';

//Cache common DOM elements
const $projRmvPlotBtn = $('.proj-rmv-plot-btn');
const $projRmvPlntlstBtn = $('.proj-rmv-plntlst-btn');
const $plotRmvPlntLstBtn = $('.plot-rmv-plntlst-btn');
const $toggleProjectsBtn = $('#toggle-projects-btn');
const $togglePlotsBtn = $('#toggle-plots-btn');
const $projectsForm = $('#add-projects-form');
const $plotsForm = $('#add-plots-form');
const $plotList = $('#plot-list');
const $projectList = $('#project-list');
const $modalBody = $('.modal-body');

// On click of X btn on connected project
$('ul').on('click', '.proj-rmv-plntlst-btn', handleRemoveProjectConn);
// On click of X btn on connected plots
$('ul').on('click', '.plot-rmv-plntlst-btn', handleRemovePlotConn);

// Toggles displaying plots add form
$togglePlotsBtn.click(function(evt) {
	$plotsForm.toggle('fast');
});
// Toggles displaying projects add form
$toggleProjectsBtn.click(function(evt) {
	$projectsForm.toggle('fast');
});

// Handles Projects - Plant Lists connections between subforms and connected lists
$projectsForm.submit(handleAddProjectSubmit);

// Handles Plots - Plant List connections between subforms and connected lists
$plotsForm.submit(handleAddPlotSubmit);

function generateOptionHTML(value, text) {
	return `
	<option value="${value}">${text}</option>
	`;
}

// Removes the project-plantlist connection, and updates connected
// projects list and project add form
function handleRemoveProjectConn(evt) {
	const $li = $(evt.currentTarget).parent();
	const plantlistId = $li.attr(dataAttrPlantListId);
	const projectId = $li.attr(dataAttrProjectId);

	Connection.projectRemovePlantList(projectId, plantlistId);
	$li.remove();

	$('#projects').append(generateOptionHTML(projectId, $li.text()));
}

// Removes the plot-plantlist connection, and updates connected
// plots list and plot add form
function handleRemovePlotConn(evt) {
	evt.preventDefault();
	const $li = $(evt.currentTarget).parent();
	const plantlistId = $li.attr(dataAttrPlantListId);
	const plotId = $li.attr(dataAttrPlotId);

	Connection.plotRemovePlantList(plotId, plantlistId);
	$li.remove();

	$('#plots').append(generateOptionHTML(plotId, $li.text()));
}

// Generates HTML for connected lists based on connection type
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

// On add project form submit updates project form and connected project
// list. Makes connection for all selected values
function handleAddProjectSubmit(evt) {
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
}
// On add plot form submit updates plot form and connected
// plot list. Makes connection for all selected values
function handleAddPlotSubmit(evt) {
	evt.preventDefault();

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
}
