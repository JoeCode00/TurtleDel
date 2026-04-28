# Turtle Delivery - Application Overview

A manufacturing and test site for high-assurance RF avionics equipment is used an example usecase for our system. In this example, products follow pipelines of fabrication, assembly, and test carried out in distinct cells distributed across a large campus. Because some cells can be a 15‑minute walk apart and each process step has variable duration and overlaps with other pipelines, the campus forms a non-trivial web of delivery routes.

This repo simulates a single instance of a larger fleet of delivery robots that are assigned routes on demand to move parts and assemblies between cells. Robots can accept deliveries in either direction to advance units through the pipeline or return units for rework based on test results. Using delivery robots reduces technician travel, shortens turnaround time, and increases throughput and operational efficiency.

## LRA9100 Example

Our implementation of this repo simulates an example pipeline for the LRA9100, a low-range altimeter product. The implementation demonstrates custom robot delivery routing between cells representing different stages in the unit pipeline.

### Pipeline Cell Mapping

- Cell0 — Robot Docking  
  Docking, charging, and robot staging.

- Cell1 — Fabrication  
  DSP PCBs are fabricated.

- Cell2 — Software Load & Verification  
  DSP PCBs are flashed with firmware and validated.

- Cell3 — Assembly & Test  
  DSP PCB is mechanically integrated with the control PCB to form the LRA9100; the completed unit undergoes final functional testing.

- Cell4 — Packing & Shipping  
  Units that pass final test are packaged and prepared for shipment.

- Cell5 — Rework  
  Units that fail testing are sent here for troubleshooting and corrective work.

---
