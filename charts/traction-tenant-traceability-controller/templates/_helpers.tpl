{{- define "global.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "global.fullname" -}}
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

{{- define "global.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "common.labels" -}}
app: {{ include "global.name" . }}
helm.sh/chart: {{ include "global.chart" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
{{- end }}

{{- define "common.selectorLabels" -}}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}


{{/* CONTROLLER */}}

{{- define "controller.fullname" -}}
{{ template "global.fullname" . }}-controller
{{- end -}}

{{- define "controller.selectorLabels" -}}
app.kubernetes.io/name: {{ include "controller.fullname" . }}
{{ include "common.selectorLabels" . }}
{{- end -}}

{{- define "controller.labels" -}}
{{ include "common.labels" . }}
{{ include "controller.selectorLabels" . }}
{{- end -}}

{{- define "controller.openshift.route.tls" -}}
insecureEdgeTerminationPolicy: {{ .Values.openshift.route.tls.insecureEdgeTerminationPolicy }}
termination: {{ .Values.openshift.route.tls.termination }}
{{- end -}}


{{/* ACAPY */}}

{{- define "acapy.fullname" -}}
{{ template "global.fullname" . }}-acapy
{{- end -}}

{{- define "acapy.labels" -}}
{{ include "common.labels" . }}
{{ include "acapy.selectorLabels" . }}
{{- end -}}

{{- define "acapy.selectorLabels" -}}
app.kubernetes.io/name: {{ include "acapy.fullname" . }}
{{ include "common.selectorLabels" . }}
{{- end -}}

{{- define "acapy.internal.admin.url" -}}
http://{{- include "acapy.fullname" . }}:{{.Values.acapy.service.adminPort }}
{{- end -}}



{{/* POSTGRESQL */}}
{{- define "global.postgresql.fullname" -}}
{{- if .Values.postgresql.fullnameOverride }}
{{- .Values.postgresql.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $postgresContext := dict "Values" .Values.postgresql "Release" .Release "Chart" (dict "Name" "postgresql") -}}
{{ template "postgresql.primary.fullname" $postgresContext }}
{{- end -}}
{{- end -}}

{{- define "postgresql.selectorLabels" -}}
app.kubernetes.io/name: {{ include "global.postgresql.fullname" . }}
{{ include "common.selectorLabels" . }}
{{- end -}}

{{- define "postgresql.labels" -}}
{{ include "common.labels" . }}
{{ include "postgresql.selectorLabels" . }}
{{- end -}}