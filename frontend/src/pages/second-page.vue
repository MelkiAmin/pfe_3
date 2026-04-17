<template>
  <VRow>
    <VCol
      cols="12"
      md="8"
    >
      <VCard
        title="Design Workspace"
        subtitle="Plan, prioritize, and launch your next event cycle."
      >
        <VCardText>
          <VTimeline
            side="end"
            density="compact"
            truncate-line="both"
          >
            <VTimelineItem
              dot-color="primary"
              size="small"
            >
              <div class="text-subtitle-2">
                Brief finalized
              </div>
              <div class="text-body-2 text-medium-emphasis">
                Align ticketing strategy and campaign goals.
              </div>
            </VTimelineItem>

            <VTimelineItem
              dot-color="warning"
              size="small"
            >
              <div class="text-subtitle-2">
                Creative in review
              </div>
              <div class="text-body-2 text-medium-emphasis">
                Landing page visuals, email headers, and social assets.
              </div>
            </VTimelineItem>

            <VTimelineItem
              dot-color="success"
              size="small"
            >
              <div class="text-subtitle-2">
                Release ready
              </div>
              <div class="text-body-2 text-medium-emphasis">
                API integrations active and checkout flow validated.
              </div>
            </VTimelineItem>
          </VTimeline>
        </VCardText>
      </VCard>
    </VCol>

    <VCol
      cols="12"
      md="4"
    >
      <VCard title="Quick Notes">
        <VCardText class="d-flex flex-column gap-3">
          <VChip
            color="primary"
            variant="tonal"
          >
            Confirm venue availability
          </VChip>
          <VChip
            color="info"
            variant="tonal"
          >
            Publish event 2 weeks early
          </VChip>
          <VChip
            color="success"
            variant="tonal"
          >
            Enable reminder notifications
          </VChip>
        </VCardText>
      </VCard>
    </VCol>
  </VRow>
</template>
