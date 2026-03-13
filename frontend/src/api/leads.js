import axios from 'axios'

const BASE = 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

export const getMetrics = () =>
  api.get('/leads/metrics').then(r => r.data)

export const getLeads = (limit = 50) =>
  api.get('/leads', { params: { limit } }).then(r => r.data.leads)

export const getEvents = (leadId = null, limit = 20) =>
  api.get('/events', { params: { lead_id: leadId, limit } }).then(r => r.data.events)

export const getLead = (id) =>
  api.get(`/leads/${id}`).then(r => r.data)

export const decideLead = (id, decision) =>
  api.post(`/leads/${id}/decide`, { decision }).then(r => r.data)

export const convertLead = (id) =>
  api.post(`/leads/${id}/convert`).then(r => r.data)

export const submitTestLead = (data) =>
  api.post('/webhook/form', data).then(r => r.data)

