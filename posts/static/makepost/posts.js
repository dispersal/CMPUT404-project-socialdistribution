function addPrivate() {
    // structure reference for each input box
    // div
    //     privateDiv
    //         removeButtonDiv
    //             removeButton
    //         appenedUrl


    let div = document.getElementById("append");
    let privateDiv = document.createElement("div");
    let testDiv = document.createElement("div");
    let removeButtonDiv = document.createElement("div");
    let removeButton = document.createElement("button");

    testDiv.className = "appendedUrl";
    removeButton.className = "btn btn-danger";
    removeButton.onclick = deleteParent;
    removeButtonDiv.className = "input-group-append";
    removeButtonDiv.appendChild(removeButton);

    let val = appendUrl();
    testDiv.innerHTML = val;
    testDiv.setAttribute("data-value", val);
    privateDiv.appendChild(testDiv);
    privateDiv.appendChild(removeButtonDiv);
    div.appendChild(privateDiv);

}

function deleteParent() {
    this.parentNode.parentNode.remove()
}

function appendUrl() {
    let input = document.getElementById("autocomplete").value;
    let list = document.getElementById("suggestedUsers");
    let children = list.children;

    for (i = 0; i < children.length; i++) {
        let child = children[i];

        if (input == child.text) {
            return child.getAttribute("data-value");
        }
    }

    return input;
}

async function getSuggestions(event) {
    let input = document.getElementById("autocomplete").value;
    let list = document.getElementById("suggestedUsers");

    list.innerHTML = "";

    let response = await fetch('/frontend/posts/searchauthor/?query=' + input);
    let users = await response.json();

    for (i = 0; i < users.length; i++) {
        let option = document.createElement('option');
        option.setAttribute("data-value", users[i]["url"]);
        option.text = users[i]["displayName"];
        list.appendChild(option);
    }
}


// not working, cant handle redirects
function submitForm() {
    let files = document.getElementById('files')
    if (files.files.length > 0) {
        let fileList = [...files.files];
        let filePromises = getFiles(fileList);
        let postPromises = filePromises.then((files) => {
            return files.map(file => postImage(file));
        });
    } else {
        makePost();
    }
}

function makePost(imageIDs = undefined) {
    let authheader = Cookies.get('authheader');
    let title = document.getElementById('title').value;
    let description = document.getElementById('description').value;
    let contentType = document.getElementById('contentType').value;
    let visibility = document.getElementById('visibility').value;
    let unlisted = document.getElementById('unlisted').checked;
    let visibleToArray = [];
    if (visibility === 'PRIVATE') {
        let visibleTo = document.getElementsByClassName('appendedUrl');
        for (let element of visibleTo) {
            visibleToArray.push(element.getAttribute("data-value"));
        }
    }
    let content = document.getElementById('content').value;
    let body = {
        title: title,
        description: description,
        content: content,
        contentType: contentType,
        unlisted: unlisted,
        visibility: visibility,
        visibleTo: visibleToArray,
    };
    fetch('/posts/', {
        method: 'post',
        headers: {
            'Authorization': `Basic ${authheader}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
    }).then((res) => {
        return res.json()
    }).then((json) => {
        console.log(json);
        window.location.href = '/frontend/posts/' + json.id
    }, (err) => {
        console.log(err)
    })
}

function postImage(fileContent) {

    let authheader = Cookies.get('authheader');
    let fileType = fileContent.split(':')[1].split(';')[0];
    fileType += ';base64';
    let formData = new FormData();
    let visibility = document.getElementById('visibility').value;
    let title = document.getElementById('title').value;
    let description = document.getElementById('description').value;
    let unlisted = document.getElementById('unlisted').checked;

    formData.append('title', title);
    formData.append('content', fileContent);
    formData.append('description', description);
    formData.append('unlisted', unlisted);
    formData.append('contentType', fileType);
    formData.append('visibility', visibility);
    if (visibility === "PRIVATE") {
        let visibleTo = document.getElementsByName('visibleTo[]');
        for (let element of visibleTo) {
            formData.append('visibleTo', element.value);
        }
    }

    fetch('/posts/', {
        method: 'post',
        body: formData,
        headers: {
            'Authorization': `Basic ${authheader}`,
        }
    }).then((res) => {
        return res.json()
    }).then((json) => {
        console.log(json);
        window.location.href = '/frontend/posts/' + json.id
    }, (err) => {
        console.log(err)
    })
}

// https://stackoverflow.com/users/1894471/dmitri-pavlutin
// https://stackoverflow.com/questions/36280818/how-to-convert-file-to-base64-in-javascript
function getBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}

function getFiles(files) {
    return Promise.all(files.map(file => getBase64(file)));
}

function checkPrivate() {
    if (document.getElementById('visibility').value === 'PRIVATE') {
        option = document.getElementById("autocomplete");
        document.getElementById('private-urls').style.display = 'block';
        option.addEventListener("input", function (event) {
            getSuggestions(event)
        });
    } else {
        document.getElementById('private-urls').style.display = 'none';
    }
}

function disable_content_input() {
    let content_input = document.getElementById('content');
    content_input.value = '';
    let content_row = document.getElementById('content-row');
    content_row.style.display = 'None';
    let content_type = document.getElementById('contentType');
    content_type.style.display = 'None';
    let text_post_button = document.getElementById('text-post');
    text_post_button.style.display = 'block';
    let content_type_label = document.getElementById('content-type-label');
    content_type_label.style.display = 'None';
}

function enable_content_input() {

    let image_input = document.getElementById('files');
    image_input.value = '';
    let content_row = document.getElementById('content-row');
    content_row.style.display = 'block';
    let content_type = document.getElementById('contentType');
    content_type.style.display = 'block';
    let text_post_button = document.getElementById('text-post');
    text_post_button.style.display = 'None';
    let content_type_label = document.getElementById('content-type-label');
    content_type_label.style.display = 'block';
}