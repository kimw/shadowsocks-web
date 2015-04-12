function onEdit () {
	for (var i = 0; i < document.querySelectorAll("INPUT").length; i++) {
		if (document.querySelectorAll("INPUT")[i].type === "text") {
			document.querySelectorAll("INPUT")[i].disabled = false;
			console.log(document.querySelectorAll("INPUT")[i]);
		};
	};
	document.getElementById("editButton").disabled = true;
	document.getElementById("saveButton").disabled = false;
	document.getElementById("cancelButton").disabled = false;
}

function onSave () {
	if (checkValue()) {
		document.getElementById("form1").submit();
	} else {
		alert("there're mistakes in one or more of the values");
	}
}

function onCancle () {
	for (var i = 0; i < document.querySelectorAll("INPUT").length; i++) {
		if (document.querySelectorAll("INPUT")[i].type === "text") {
			document.querySelectorAll("INPUT")[i].disabled = true;
			console.log(document.querySelectorAll("INPUT")[i]);
		};
	};
	document.getElementById("editButton").disabled = false;
	document.getElementById("saveButton").disabled = true;
	document.getElementById("cancelButton").disabled = true;
}

function checkValue () {
	function isInteger (n) {
		return !isNaN(n)
	}

	// TODO: check ip address
	document.getElementById("server").value;

	// check crypt method
	valid_methods = ["aes-128-cfb", "aes-192-cfb", "aes-256-cfb",
		"aes-128-ofb", "aes-192-ofb", "aes-256-ofb", "aes-128-ctr",
		"aes-192-ctr", "aes-256-ctr", "aes-128-cfb8", "aes-192-cfb8",
		"aes-256-cfb8", "aes-128-cfb1", "aes-192-cfb1", "aes-256-cfb1",
		"bf-cfb", "camellia-128-cfb", "camellia-192-cfb",
		"camellia-256-cfb", "cast5-cfb", "chacha20", "des-cfb", "idea-cfb",
		"rc2-cfb", "rc4", "rc4-md5", "salsa20", "seed-cfb", "table"]
	if (valid_methods.indexOf(document.getElementById("method").value) == -1) {
		console.log("wrong crypt method")
		return false;
	}

	// timout is an integer, and not less than 300
	v = document.getElementById("timeout").value
	if (!isInteger(v) || v < 300) {
		console.log("wrong timeout")
		return false;
	}

	// workers is an integer, and not less than 1
	v = document.getElementById("workers").value
	if (!isInteger(v) || v < 1) {
		console.log("wrong workers")
		return false;
	}

	for (var i = 0; i < document.getElementsByName("port").length; i++) {
		port = document.getElementsByName("port")[i].value;
		if (!isInteger(port) || port > 65535) {
			console.log("wrong port")
			return false;
		}
	}

	return true;
}

function show_qrcode(id) {
	target = document.getElementById(id);
	console.log("target.style.visibility=", target.style.visibility)
	if (target.style.visibility == "") {
		console.log("target.style.visibility == null")
		target.style.visibility = "hidden"
	}
	if (target.style.visibility == "visible") {
		target.style.visibility = "hidden";
		console.log("target.style.visibility=", target.style.visibility)
	} else if (target.style.visibility == "hidden") {
		target.style.visibility = "visible";
		console.log("target.style.visibility=", target.style.visibility)
	}
}
