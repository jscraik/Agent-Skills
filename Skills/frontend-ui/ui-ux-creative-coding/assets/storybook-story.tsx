import type { Meta, StoryObj } from "@storybook/react";
// import { within, userEvent, expect } from "@storybook/test";
// import { MyComponent } from "./my-component";

const meta: Meta/* <typeof MyComponent> */ = {
  title: "ui/MyComponent",
  // component: MyComponent,
  parameters: {
    layout: "centered",
    // For Argos stability:
    // - avoid nondeterministic animation
    // - use fixed data/fixtures
  },
  args: {},
};
export default meta;

type Story = StoryObj/* <typeof MyComponent> */;

export const Default: Story = {
  args: {},
};

export const States: Story = {
  args: {},
  render: (args) => {
    return (
      <div className="grid gap-4">
        {/* Render variants/states side-by-side for visual regression */}
        <div className="text-sm text-neutral-600">Default</div>
        <div>{/* <MyComponent {...args} /> */}</div>

        <div className="text-sm text-neutral-600">Disabled</div>
        <div>{/* <MyComponent {...args} disabled /> */}</div>

        <div className="text-sm text-neutral-600">Loading</div>
        <div>{/* <MyComponent {...args} loading /> */}</div>
      </div>
    );
  },
};

// Optional: deterministic interaction test (only if stable).
// export const Interaction: Story = {
//   play: async ({ canvasElement }) => {
//     const canvas = within(canvasElement);
//     await userEvent.click(canvas.getByRole("button", { name: /submit/i }));
//     await expect(canvas.getByText(/success/i)).toBeInTheDocument();
//   },
// };
