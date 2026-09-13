/*
 * Copyright (c) 2026 DuckDuckGo
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.duckduckgo.app.browser.nativeinput

import android.net.Uri
import android.view.LayoutInflater
import android.view.ViewGroup
import android.webkit.ValueCallback
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.LiveData
import com.duckduckgo.app.browser.omnibar.Omnibar
import com.duckduckgo.app.tabs.model.TabEntity
import com.duckduckgo.browser.api.autocomplete.AutoComplete.AutoCompleteSuggestion
import com.duckduckgo.di.scopes.FragmentScope
import com.squareup.anvil.annotations.ContributesBinding
import kotlinx.coroutines.flow.Flow
import org.json.JSONArray
import javax.inject.Inject

class NativeInputCallbacks(
    val onSearchTextChanged: (String) -> Unit,
    val onSearchSubmitted: (String) -> Unit,
    val onDuckAiChatSubmitted: (
        query: String,
        modelId: String?,
        reasoningEffort: String?,
        selectedTool: String?,
        imagesJson: JSONArray?,
        filesJson: JSONArray?,
    ) -> Unit = { _, _, _, _, _, _ -> },
    val onChatSuggestionSelected: (String) -> Unit = {},
    /** User picked a model in the native picker (→ submitChangeModelAction). */
    val onChangeModelSubmitted: (modelId: String) -> Unit = {},
    val onCustomizeResponsesClicked: () -> Unit = {},
    val onChatUrlSuggestionClicked: (AutoCompleteSuggestion) -> Unit = {},
    val onChatHistoryShortcutClicked: () -> Unit = {},
    val onChatSuggestionDelete: (chatUrl: String) -> Unit = {},
    val onClearAutocomplete: () -> Unit,
    val onStopTapped: () -> Unit = {},
    val onFireButtonPressed: () -> Unit = {},
    val onTabSwitcherPressed: () -> Unit = {},
    val onBrowserMenuPressed: () -> Unit = {},
    val onVoiceSearchPressed: (isChatTab: Boolean) -> Unit = {},
    val onCameraCaptureRequested: (ValueCallback<Array<Uri>>) -> Unit = {},
    val onFilePickerRequested: (ValueCallback<Array<Uri>>, List<String>) -> Unit = { _, _ -> },
    /**
     * Restore the autocomplete view state from the always-on cache the viewmodel keeps for
     * the omnibar's text. Returns true when the cache matched [forQuery] and was applied;
     * the caller uses the return value to decide whether to re-show the suggestions list.
     */
    val restoreOmnibarAutocomplete: (forQuery: String) -> Boolean = { _ -> false },
)

interface NativeInputManager {
    fun init(
        omnibar: Omnibar,
        rootView: ViewGroup,
        lifecycleOwner: LifecycleOwner,
        onDisabled: () -> Unit = {},
    )

    fun isNativeInputEnabled(): Boolean

    /**
     * Whether the native input should actually be used for the current context, as opposed to the
     * legacy omnibar.
     */
    fun isNativeInputActive(): Boolean

    /** True when the native input widget is currently attached (top or bottom omnibar). */
    fun isNativeInputShown(): Boolean

    /** True when the widget is shown with the chat tab selected. */
    fun isChatTabSelected(): Boolean

    fun showNativeInput(
        tabId: String,
        layoutInflater: LayoutInflater,
        lifecycleOwner: LifecycleOwner,
        tabs: LiveData<List<TabEntity>>,
        currentTabUrl: Flow<String?>,
        query: String = "",
        callbacks: NativeInputCallbacks,
    )

    fun hideNativeInput(animate: Boolean = true, isNavigation: Boolean = false): Boolean
    fun onKeyboardVisibilityChanged(isVisible: Boolean)
    fun setPickingImage(picking: Boolean)
    fun setText(text: String)

    fun refreshChatSuggestions()

    /** The user confirmed deleting a recent chat from the chat-autocomplete fire dialog. */
    fun onChatDeleteConfirmed()

    /** The user cancelled deleting a recent chat from the chat-autocomplete fire dialog. */
    fun onChatDeleteCancelled()

    /** Show pulse animation around the fire button. */
    fun setDuckAiFireButtonHighlighted(highlighted: Boolean)

    /** Hide/show the subscription-tier indicator in the header. */
    fun setDuckAiTierVisible(visible: Boolean)
}

/**
 * No-op native input manager. The Duck.ai native input field has been removed from the app, so the
 * omnibar always falls back to the legacy text input.
 */
@ContributesBinding(FragmentScope::class)
class RealNativeInputManager @Inject constructor() : NativeInputManager {

    override fun init(
        omnibar: Omnibar,
        rootView: ViewGroup,
        lifecycleOwner: LifecycleOwner,
        onDisabled: () -> Unit,
    ) {
        // no-op
    }

    override fun isNativeInputEnabled(): Boolean = false

    override fun isNativeInputActive(): Boolean = false

    override fun isNativeInputShown(): Boolean = false

    override fun isChatTabSelected(): Boolean = false

    override fun showNativeInput(
        tabId: String,
        layoutInflater: LayoutInflater,
        lifecycleOwner: LifecycleOwner,
        tabs: LiveData<List<TabEntity>>,
        currentTabUrl: Flow<String?>,
        query: String,
        callbacks: NativeInputCallbacks,
    ) {
        // no-op
    }

    override fun hideNativeInput(animate: Boolean, isNavigation: Boolean): Boolean = false

    override fun onKeyboardVisibilityChanged(isVisible: Boolean) {
        // no-op
    }

    override fun setPickingImage(picking: Boolean) {
        // no-op
    }

    override fun setText(text: String) {
        // no-op
    }

    override fun refreshChatSuggestions() {
        // no-op
    }

    override fun onChatDeleteConfirmed() {
        // no-op
    }

    override fun onChatDeleteCancelled() {
        // no-op
    }

    override fun setDuckAiFireButtonHighlighted(highlighted: Boolean) {
        // no-op
    }

    override fun setDuckAiTierVisible(visible: Boolean) {
        // no-op
    }
}
