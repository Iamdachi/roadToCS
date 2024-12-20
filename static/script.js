let zoom = d3.zoom()
	.scaleExtent([0.25, 10])
	.on('zoom', handleZoom);


function initZoom() {
  d3.select('svg')
    .call(zoom);
}

function handleZoom(e) {
	d3.select('svg g')
		.attr('transform', e.transform);
}

function handleCheckboxClick(checkbox) {
  const lectureId = checkbox.getAttribute('id');
  console.log(lectureId);
  const isChecked = checkbox.checked;

  fetch('/update-lecture-status', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      lecture_id: lectureId,
      done: isChecked,
    }),
  })
  .then(response => response.json())
  .then(data => {
    console.log('Success:', data);
  })
  .catch((error) => {
    console.error('Error:', error);
  });
}


function draw(data, lectures) {
  const svgGroup = d3.select('svg g');
  svgGroup
    .selectAll('rect')
    .data(data)
    .join(
      enter => enter
        .append("g") // Append group to contain each element
        .each(function(d, i) {
          const group = d3.select(this);

          // Main rectangle
          group.append("rect")
            .attr('x', d.x)
            .attr('y', d.y)
            .attr('width', 250)
            .attr('height', 80)
            .attr('fill', 'rgb(123, 24, 40)')
            .attr('rx', 20)
            .attr('ry', 20)
            .attr('id', `n${i}`)
            .on('click', function(event, d) {
              d3.select('#sidebar')
                .classed('active', true);

              d3.select('#sidebar h2').text(d.title);

              const ul = d3.select('#sidebar ul');
              ul.selectAll('li').remove();

              const lectureItems = lectures[d.id];
              if (lectureItems) {
                ul.selectAll('li')
                  .data(lectureItems)
                  .enter()
                  .append('li')
                  .each(function(lecture) {
                    const li = d3.select(this);
                    li.append('input')
                      .attr('type', 'checkbox')
                      .attr('class', 'lecture-checkbox')
                      .attr('id', `L${d.id}_${lecture.id}`) // Set unique id
                      .property('checked', lecture.done)
                      .on('change', function() {
                        const checkboxes = ul.selectAll('.lecture-checkbox');
                        const checkedCount = checkboxes.filter(':checked').size();
                        const totalLectures = checkboxes.size();
                        const progress = (checkedCount / totalLectures) * 230;

                        d3.select(`.progress-bar-${d.id}`)
                          .attr('width', progress);

                        // send request

                        handleCheckboxClick(this);
                      });

                    li.append('a')
                      .attr('href', lecture.link)
                      .attr('target', '_blank')
                      .text(lecture.title);
                  });
              } else {
                console.error(`No lectures found for id: ${d.id}`);
              }
            });

          // Title inside rectangle
          group.append("text")
            .attr("x", d.x + 125)
            .attr("y", d.y + 40)
            .attr("fill", "white")
            .attr("text-anchor", "middle")
            .style("font-family", "Roboto")
            .style("font-weight", "bold")
            .text(d.title);

          // Draw triangle (for id > 0)
          if (i > 0) {
            group.append("polygon")
              .attr("points", `${d.x + 125 - 15},${d.y - 20} ${d.x + 125 + 15},${d.y - 20} ${d.x + 125},${d.y}`)
              .attr("fill", "white");
          }

          // Progress bar (background and actual bar)
          group.append("rect")
            .attr('x', d.x + 10)
            .attr('y', d.y + 60)
            .attr('width', 230)
            .attr('height', 10)
            .attr('fill', 'white')
            .attr('rx', 5)
            .attr('ry', 5);

          group.append("rect")
            .attr('x', d.x + 10)
            .attr('y', d.y + 60)
            .attr('width', 0)
            .attr('height', 10)
            .attr('fill', 'green')
            .attr('rx', 5)
            .attr('ry', 5)
            .attr('class', `progress-bar-${i}`);


            // After appending all checkboxes and setting their 'checked' property
            let checkedCount = 0;
            lectures[d.id].forEach(entry => {
              if (entry["done"]) checkedCount++;
            });

            const totalLectures = lectures[d.id].length;
            const progress = (checkedCount / totalLectures) * 230;

          d3.select(`.progress-bar-${i}`)
            .attr('width', progress);
        })
    );

  // Close sidebar when "esc" button is clicked
  d3.select('#close-btn').on('click', function() {
    d3.select('#sidebar')
      .classed('active', false);
  });
}


function drawPaths(paths) {
  // Calculate bezier curve for each path
  const coordinates = [];
  paths.forEach(path => {
    // Start x y
        let x = d3.select(`#${path[0]}`).attr('x');
        let widthOne = d3.select(`#${path[0]}`).attr('width');
        let y = d3.select(`#${path[0]}`).attr('y');
        const height1 = d3.select(`#${path[0]}`).attr('height');
        x = parseInt(x) + parseInt(widthOne) / 2;
        y = parseInt(y) + parseInt(height1);

        // End x y
        let ex = d3.select(`#${path[1]}`).attr('x'); // Use escape for a single digit
        let ey = d3.select(`#${path[1]}`).attr('y');
        let width2 = d3.select(`#${path[0]}`).attr('width');
        ex = parseInt(ex) + parseInt(width2) / 2;


    // Check if any coordinate is null
    if (x !== null && y !== null && ex !== null && ey !== null) {
      const pathString = `M ${x} ${y} C ${x} ${y+50}, ${ex} ${ey-60}, ${ex} ${ey-20}`;
      coordinates.push(pathString);
    } else {
      console.warn("Could not find coordinates for path:", path);
    }
  });

  d3.select('svg g')
    .selectAll('path')
    .data(coordinates)
    .join('path')
    .attr('d', function(d) { return d; }) // Set the 'd' attribute for the path
    .attr('fill', 'none') // No fill for the curve
    .attr('stroke', 'white') // Stroke color
    .attr('stroke-width', 2); // Stroke width
}

initZoom();

document.addEventListener("DOMContentLoaded", () => {
  Promise.all([
    fetch('/mit-lectures').then(response => response.json()),
    fetch('/mit-roadmap').then(response => response.json())
  ]).then(([lecturesResponse, roadmapResponse]) => {
    const lectures = lecturesResponse;
    const data = roadmapResponse.data;
    const paths = roadmapResponse.paths;

    draw(data, lectures); // Now `lectures` is guaranteed to be available
    setTimeout(() => drawPaths(paths), 0); // Ensure paths are drawn after rects
  }).catch(error => {
    console.error("Error loading data:", error);
  });
});


