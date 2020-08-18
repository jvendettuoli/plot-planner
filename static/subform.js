'use strict';

console.log('START subform.js');

//Cache common DOM elements
const $toggleProjectsBtn = $('#toggle-projects-btn');
const $togglePlotsBtn = $('#toggle-plots-btn');
const $projectsForm = $('#add-projects-form');
const $plotsForm = $('#add-plots-form');
const $plotList = $('#plot-list');
const $projectList = $('#project-list');
const $modalBody = $('.modal-body');

function generateLiHTML(element, plantlistId, elementId, elementName) {
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

	const plantlistId = $(evt.currentTarget).parent().attr(dataAttrPlantListId);
	let serializedInputs = $(this).serializeArray();

	// For each input, connect the project and plantlist, and update the Connected Projects list and Projects form to reflect the new connection.
	serializedInputs.forEach((element) => {
		if (element.name !== 'csrf_token') {
			Connection.projectAddPlantList(element.value, plantlistId);
			const optionText = $(`option:selected[value='${element.value}']`).text();
			if ($projectList.text().includes('No projects connected yet.')) {
				$projectList.empty();
			}
			$projectList.append(generateLiHTML('project', plantlistId, element.value, optionText));
			$(`option:selected[value='${element.value}']`).remove();
		}
	});
});
// Handles Projects - Plot connections between subforms and connected lists

$modalBody.on('submit', function(evt) {
	evt.preventDefault();
	console.log('Proj-PLOTFORM');
	console.log('event', evt);

	const projectId = $(evt.currentTarget).attr(dataAttrProjectId);
	console.log('evet target', evt.currentTarget);
	console.log('ProjectID', projectId);
	let serializedInputs = $(this).children('form').serializeArray();
	console.log(serializedInputs);

	// For each input, connect the plot and plantlist, and update the Connected Plots list and Plots form to reflect the new connection.
	serializedInputs.forEach((element) => {
		if (element.name !== 'csrf_token') {
			Connection.projectAddPlot(projectId, element.value);
			const optionText = $(`option:selected[value='${element.value}']`).text();
			if ($plotList.text().includes('No plots connected yet.')) {
				$plotList.empty();
			}
			console.log($(`#plot-list-${projectId}`));
			$(`#plot-list-${projectId}`).append(generateLiHTML('plot', projectId, element.value, optionText));
			$(`option:selected[value='${element.value}']`).remove();
		}
	});
});

// Handles Plots - Plant List connections between subforms and connected lists
$plotsForm.submit(function(evt) {
	evt.preventDefault();
	console.log('PLOTFORM');

	const plantlistId = $(evt.currentTarget).parent().attr(dataAttrPlantListId);
	let serializedInputs = $(this).serializeArray();

	// For each input, connect the plot and plantlist, and update the Connected Plots list and Plots form to reflect the new connection.
	serializedInputs.forEach((element) => {
		if (element.name !== 'csrf_token') {
			Connection.plotAddPlantList(element.value, plantlistId);
			const optionText = $(`option:selected[value='${element.value}']`).text();
			if ($plotList.text().includes('No plots connected yet.')) {
				$plotList.empty();
			}
			$plotList.append(generateLiHTML('plot', plantlistId, element.value, optionText));
			$(`option:selected[value='${element.value}']`).remove();
		}
	});
});
