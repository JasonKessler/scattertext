// Adapted from https://www.w3schools.com/howto/howto_js_autocomplete.asp
function autocomplete(inputField, autocompleteValues, myPlotInterface) {
    var currentFocus; // current position in autocomplete list.

    inputField.addEventListener("input", function (e) {
        var matchedCandidateListDiv, matchedCandidateDiv, i, userInput = this.value;

        closeAllLists();
        if (!userInput) {
            return false;
        }
        currentFocus = -1;

        matchedCandidateListDiv = document.createElement("div");
        matchedCandidateListDiv.setAttribute("id", this.id + "autocomplete-list");
        matchedCandidateListDiv.setAttribute("class", "autocomplete-items");

        this.parentNode.appendChild(matchedCandidateListDiv);
        autocompleteValues.map(function (candidate) {
            var candidatePrefix = candidate.substr(0, userInput.length);
            if (candidatePrefix.toLowerCase() === userInput.toLowerCase()) {
                matchedCandidateDiv = document.createElement("div");
                matchedCandidateDiv.innerHTML = "<strong>" + candidatePrefix + "</strong>";
                matchedCandidateDiv.innerHTML += candidate.substr(userInput.length);
                matchedCandidateDiv.innerHTML += "<input type='hidden' value='" + candidate + "'>";
                matchedCandidateDiv.addEventListener("click", function (e) {
                    inputField.value = this.getElementsByTagName("input")[0].value;
                    closeAllLists();
                    myPlotInterface.handleSearchTerm(inputField.value);
                });
                matchedCandidateListDiv.appendChild(matchedCandidateDiv);
            }
        });
    });

    inputField.addEventListener("keydown", function (keyboardEvent) {

        var candidateDivList = document.getElementById(this.id + "autocomplete-list");

        if (!candidateDivList)
            return true;

        var selectedCandidate = Array.prototype.find.call(
            candidateDivList.children,
            x => x.className !== ""
        );

        if (keyboardEvent.keyCode === 40 || keyboardEvent.keyCode === 9) { // down or tab
            keyboardEvent.preventDefault();
            currentFocus++;
            addActive(candidateDivList.getElementsByTagName("div"));
        } else if (keyboardEvent.keyCode === 38) { //up
            currentFocus--;
            addActive(candidateDivList.getElementsByTagName("div"));
        } else if (keyboardEvent.keyCode === 13) { // enter
            keyboardEvent.preventDefault();
            var selectedTerm = inputField.value;
            console.log("selected term");console.log(selectedTerm);
            console.log(myPlotInterface);
            //if (selectedCandidate)
            //    selectedTerm = selectedCandidate.children[1].value;
            myPlotInterface.handleSearchTerm(selectedTerm);
            closeAllLists(null);
        } else if (keyboardEvent.keyCode === 27) { // esc
            closeAllLists(null);
        }
    });

    function addActive(candidateDivList) {
        if (!candidateDivList) return false;

        removeActive(candidateDivList);

        if (currentFocus >= candidateDivList.length)
            currentFocus = 0;
        if (currentFocus < 0)
            currentFocus = (candidateDivList.length - 1);

        candidateDivList[currentFocus].classList.add("autocomplete-active");

        var selectedCandidate = Array.prototype.find.call(
            candidateDivList,
            x => x.className !== ""
        );

        if (selectedCandidate) {
            var candidateValue = selectedCandidate.children[1].value;
            myPlotInterface.highlightTerm(candidateValue);
            inputField.value = candidateValue;
        }

    }

    function removeActive(candidateDivList) {
        Array.prototype.find.call(
            candidateDivList,
            x => x.classList.remove("autocomplete-active")
        );
    }

    function closeAllLists(elmnt) {
        /*close all autocomplete lists in the document,
        except the one passed as an argument:*/
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inputField) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }

    /*execute a function when someone clicks in the document:*/
    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });
}
