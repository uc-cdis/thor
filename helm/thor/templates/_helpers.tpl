{{/*
Expand the name of the chart.
*/}}
{{- define "thor.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "thor.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "thor.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "thor.labels" -}}
{{- if .Values.commonLabels }}
    {{- with .Values.commonLabels }}
    {{- toYaml . }}
    {{- end }}
{{- else }}
  {{- (include "common.commonLabels" .)}}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "thor.selectorLabels" -}}
{{- if .Values.selectorLabels }}
    {{- with .Values.selectorLabels }}
    {{- toYaml . }}
    {{- end }}
{{- else }}
  {{- (include "common.selectorLabels" .)}}
{{- end }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "thor.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "thor.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}


{{/*
    Gen3 Chart Labels
    Will use the parent chart's chart, release, and version as well as the values "release", "criticalService", and "partOf" defined in the values.yaml file.
    These values can be completely overwritten with the "selectorLabels" and "commonLabels" provided in the parent chart's values.yaml file.
    "selectorLabels" are mainly used for the matchLabels and pod labels in the deployment.
    "commonLabels" are mainly used for the deployment's labels.
*/}}

{{- define "common.commonLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.Version }}
app.kubernetes.io/part-of: {{ .Values.partOf }}
app.kubernetes.io/managed-by: "Helm"
app: {{ .Chart.Name }}
{{- if eq .Values.criticalService "true"}}
critical-service: "true"
{{- else }}
critical-service: "false"
{{- end }}
{{- if eq .Values.release "production"}}
release: "production"
{{- else }}
release: "dev"
{{- end }}
{{- end }}

{{- define "common.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app: {{ .Chart.Name }}
{{- if eq .Values.release "production"}}
release: "production"
{{- else }}
release: "dev"
{{- end }}
{{- end }}
