import {patch} from '@web/core/utils/patch';
import {CustomerAddress} from '@portal/interactions/address';
import {rpc} from '@web/core/network/rpc';

patch(CustomerAddress.prototype, {

    setup() {
        // Call original setup
        super.setup();
        if (!this.requiredFields.includes('township_id')) {
            this.requiredFields.push('township_id');
        }

        // Add township change listener
        this.dynamicContent = {
            ...this.dynamicContent,
            'select[name="township_id"]': {'t-on-change': this.onChangeTownship},
        };
    },

    async willStart() {
        super.willStart()
        await this._onChangeState(true)
    },
    async onChangeTownship() {
    },

    async onChangeState() {
        super.onChangeState()
        return this._onChangeState();
    },

    async _onChangeState(init = false) {
        const stateId = parseInt(this.addressForm.state_id.value);
        const data = await this.waitFor(rpc(
            `/my/address/state_info/${stateId}`
        ));
        const selectTownship = this.addressForm.township_id;

        if (!init || selectTownship.options.length === 1) {
            // dont reload state at first loading (done in qweb)
            if (data.townships.length) {
                // empty existing options, only keep the placeholder.
                selectTownship.options.length = 1;

                // create new options and append them to the select element
                data.townships.forEach((tsp) => {
                    const state_option = new Option(tsp[1], tsp[0]);
                    selectTownship.appendChild(state_option);
                });
                this._showInput('township_id');
            } else {
                this._hideInput('township_id');
            }
        }
    }
});