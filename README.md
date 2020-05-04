# openspace

## Einführung

openspace basiert im Allgemeinen auf den Komponenten *OpenSubmit* und *Jenkins* und wird auf *OpenShift* ausgeführt.

### OpenSubmit

*"This is OpenSubmit, a small web application for managing student assignment solutions in a university environment"* (https://github.com/troeger/opensubmit).

OpenSubmit ist im wesentlichen eine Platform um Abgaben von Studierenden automatisiert zu testen und zu managen. Sie besteht aus zwei teilen.

- **executor** führt Tests auf Abgaben von Studierenden aus.
- **web** ist die Web-Oberfläche. Hier können Studierende ihre Abgaben hochladen und Dozenten diese auf einer separaten Administrations-Seite managen.

OpenSubmit ist ausführlich dokumentiert. Auf folgendem Link können weitere Details zur Struktur und zum Nutzen der Web-Oberfläche gefunden werden (http://docs.open-submit.org/en/latest).

### Jenkins

*"Jenkins is a self-contained, open source automation server which can be used to automate all sorts of tasks related to building, testing, and delivering or deploying software"* (https://jenkins.io/doc).
Ursprünglich sollen Tests der Abgaben durch den executor von OpenSubmit durchgeführt werden. Da dieser das mit einem Python Script macht wird Jenkins benutzt um in das Testing mehr Variabilität zu bringen. Der executor führt also nicht mehr nur Tests aus, sondern deligiert diese weiter an die Jenkins Komponente.

### OpenShift

*"OKD is a distribution of Kubernetes optimized for continuous application development and multi-tenant deployment"* (https://docs.okd.io).
OpenShift dient als Platform um die Systeme OpenSubmit und Jenkins auszuführen.

## Installation

Um die Systeme auf OpenShift zu installieren, existiert im Repository ein OpenShift Template.
Das hochschulweite OpenShift ist über folgenden Link erreichbar: https://console.k8s.fbi.h-da.de:8443/console.
Hier kann das OpenShift Template in ein neues oder vorhandenes Projekt importiert werden (*Import YAML / JSON*).
Bei Import wird nach verschiedenen Parametern gefragt. Zu allen Parametern sollten Details während der Eingabe stehen.

## Assignments