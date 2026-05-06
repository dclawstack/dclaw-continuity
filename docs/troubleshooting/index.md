# Troubleshooting

Common issues and solutions for DClaw Continuity.

## Quick Diagnostics

```bash
# Check app pods
kubectl get pods -n dclaw-continuity

# Check logs
kubectl logs -n dclaw-continuity deployment/dclaw-continuity-backend

# Check database
kubectl get clusters -n dclaw-continuity
```

## Sections

- [Common Issues](./common-issues)
- [FAQ](./faq)
